import types
import pytest

from structkit import filters

SHA_1 = "1" * 40
SHA_2 = "2" * 40
SHA_3 = "3" * 40


@pytest.fixture(autouse=True)
def clear_filter_cache():
    filters.cache.clear()


def install_fake_repo(monkeypatch, repo):
    class FakeGithub:
        def __init__(self, token=None):
            self.token = token

        def get_repo(self, name):
            assert name == "owner/repo"
            return repo

    monkeypatch.setattr(filters, "Github", FakeGithub)


def git_object(object_type, sha):
    return types.SimpleNamespace(type=object_type, sha=sha)


def test_slugify_basic():
    assert filters.slugify("Hello World!") == "hello-world"
    assert filters.slugify("Already-Slugified_123") == "already-slugified123"


def test_get_default_branch_success(monkeypatch):
    # Build a minimal fake Github client
    class FakeRepo:
        default_branch = "main"

    class FakeGithub:
        def __init__(self, token=None):
            self.token = token

        def get_repo(self, name):
            assert name == "owner/repo"
            return FakeRepo()

    monkeypatch.setenv("GITHUB_TOKEN", "tok")
    monkeypatch.setattr(filters, "Github", FakeGithub)

    assert filters.get_default_branch("owner/repo") == "main"


def test_get_default_branch_error(monkeypatch):
    class FakeGithub:
        def get_repo(self, name):
            raise Exception("boom")

    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setattr(filters, "Github", FakeGithub)
    filters.cache.clear()

    assert filters.get_default_branch("owner/repo") == "DEFAULT_BRANCH_ERROR"


def test_get_latest_release_success(monkeypatch):
    class FakeRepo:
        default_branch = "dev"

        def get_latest_release(self):
            class R:
                tag_name = "v1.2.3"

            return R()

    class FakeGithub:
        def __init__(self, token=None):
            pass

        def get_repo(self, name):
            return FakeRepo()

    monkeypatch.setattr(filters, "Github", FakeGithub)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    # Clear cache between tests to ensure function recomputes
    filters.cache.clear()

    assert filters.get_latest_release("owner/repo") == "v1.2.3"


@pytest.mark.parametrize(
    ("tag_name", "expected"),
    [
        ("v1.2.3", "1.2.3"),
        ("vv1.2.3", "v1.2.3"),
        ("1.2.3", "1.2.3"),
        ("V1.2.3", "V1.2.3"),
    ],
)
def test_get_latest_release_strip_v(monkeypatch, tag_name, expected):
    repo = types.SimpleNamespace(
        get_latest_release=lambda: types.SimpleNamespace(tag_name=tag_name)
    )
    install_fake_repo(monkeypatch, repo)

    assert filters.get_latest_release("owner/repo", strip_v=True) == expected


def test_get_latest_release_strip_v_disabled(monkeypatch):
    repo = types.SimpleNamespace(
        get_latest_release=lambda: types.SimpleNamespace(tag_name="v1.2.3")
    )
    install_fake_repo(monkeypatch, repo)

    assert filters.get_latest_release("owner/repo", strip_v=False) == "v1.2.3"


def test_get_latest_release_lightweight_tag_sha(monkeypatch):
    class FakeRepo:
        def get_latest_release(self):
            return types.SimpleNamespace(tag_name="v1.2.3")

        def get_git_ref(self, ref):
            assert ref == "tags/v1.2.3"
            return types.SimpleNamespace(object=git_object("commit", SHA_1))

    install_fake_repo(monkeypatch, FakeRepo())

    assert filters.get_latest_release("owner/repo", return_sha=True) == SHA_1


def test_get_latest_release_annotated_tag_sha(monkeypatch):
    class FakeRepo:
        def get_latest_release(self):
            return types.SimpleNamespace(tag_name="v1.2.3")

        def get_git_ref(self, ref):
            assert ref == "tags/v1.2.3"
            return types.SimpleNamespace(object=git_object("tag", SHA_1))

        def get_git_tag(self, sha):
            assert sha == SHA_1
            return types.SimpleNamespace(object=git_object("commit", SHA_2))

    install_fake_repo(monkeypatch, FakeRepo())

    assert filters.get_latest_release("owner/repo", return_sha=True) == SHA_2


def test_get_latest_release_nested_annotated_tag_sha(monkeypatch):
    class FakeRepo:
        def get_latest_release(self):
            return types.SimpleNamespace(tag_name="v1.2.3")

        def get_git_ref(self, ref):
            return types.SimpleNamespace(object=git_object("tag", SHA_1))

        def get_git_tag(self, sha):
            objects = {
                SHA_1: git_object("tag", SHA_2),
                SHA_2: git_object("commit", SHA_3),
            }
            return types.SimpleNamespace(object=objects[sha])

    install_fake_repo(monkeypatch, FakeRepo())

    assert filters.get_latest_release("owner/repo", return_sha=True) == SHA_3


def test_return_sha_takes_precedence_over_strip_v(monkeypatch):
    repo = types.SimpleNamespace(
        get_latest_release=lambda: types.SimpleNamespace(tag_name="v1.2.3"),
        get_git_ref=lambda ref: types.SimpleNamespace(
            object=git_object("commit", SHA_1)
        ),
    )
    install_fake_repo(monkeypatch, repo)

    assert (
        filters.get_latest_release("owner/repo", strip_v=True, return_sha=True) == SHA_1
    )


def test_get_latest_release_falls_back_to_default_branch(monkeypatch):
    class FakeRepo:
        default_branch = "main"

        def get_latest_release(self):
            raise Exception("no releases")

    class FakeGithub:
        def __init__(self, token=None):
            pass

        def get_repo(self, name):
            return FakeRepo()

    monkeypatch.setattr(filters, "Github", FakeGithub)
    filters.cache.clear()

    assert filters.get_latest_release("owner/repo") == "main"


def test_strip_v_does_not_change_default_branch_fallback(monkeypatch):
    repo = types.SimpleNamespace(
        default_branch="v-main",
        get_latest_release=lambda: (_ for _ in ()).throw(Exception("no releases")),
    )
    install_fake_repo(monkeypatch, repo)

    assert filters.get_latest_release("owner/repo", strip_v=True) == "v-main"


def test_release_failure_falls_back_to_default_branch_sha(monkeypatch):
    class FakeRepo:
        default_branch = "main"

        def get_latest_release(self):
            raise Exception("no releases")

        def get_git_ref(self, ref):
            assert ref == "heads/main"
            return types.SimpleNamespace(object=git_object("commit", SHA_1))

    install_fake_repo(monkeypatch, FakeRepo())

    assert filters.get_latest_release("owner/repo", return_sha=True) == SHA_1


@pytest.mark.parametrize(
    "git_ref",
    [
        None,
        types.SimpleNamespace(object=None),
        types.SimpleNamespace(object=git_object(None, SHA_1)),
        types.SimpleNamespace(object=git_object("commit", None)),
        types.SimpleNamespace(object=git_object("commit", "not-a-sha")),
        types.SimpleNamespace(object=git_object("tree", SHA_1)),
    ],
)
def test_malformed_release_git_data_returns_error(monkeypatch, git_ref):
    class FakeRepo:
        def get_latest_release(self):
            return types.SimpleNamespace(tag_name="v1.2.3")

        def get_git_ref(self, ref):
            return git_ref

    install_fake_repo(monkeypatch, FakeRepo())

    assert (
        filters.get_latest_release("owner/repo", return_sha=True)
        == "LATEST_RELEASE_ERROR"
    )


@pytest.mark.parametrize("tag_name", [None, "", 123])
def test_malformed_release_tag_name_returns_error(monkeypatch, tag_name):
    repo = types.SimpleNamespace(
        get_latest_release=lambda: types.SimpleNamespace(tag_name=tag_name)
    )
    install_fake_repo(monkeypatch, repo)

    assert filters.get_latest_release("owner/repo") == "LATEST_RELEASE_ERROR"


def test_release_tag_name_lookup_failure_returns_error(monkeypatch):
    class FakeRelease:
        @property
        def tag_name(self):
            raise Exception("malformed release")

    repo = types.SimpleNamespace(get_latest_release=lambda: FakeRelease())
    install_fake_repo(monkeypatch, repo)

    assert filters.get_latest_release("owner/repo") == "LATEST_RELEASE_ERROR"


def test_annotated_tag_cycle_returns_error(monkeypatch):
    class FakeRepo:
        def get_latest_release(self):
            return types.SimpleNamespace(tag_name="v1.2.3")

        def get_git_ref(self, ref):
            return types.SimpleNamespace(object=git_object("tag", SHA_1))

        def get_git_tag(self, sha):
            return types.SimpleNamespace(object=git_object("tag", SHA_1))

    install_fake_repo(monkeypatch, FakeRepo())

    assert (
        filters.get_latest_release("owner/repo", return_sha=True)
        == "LATEST_RELEASE_ERROR"
    )


def test_selected_release_sha_lookup_failure_does_not_fallback(monkeypatch):
    class FakeRepo:
        default_branch = "main"

        def get_latest_release(self):
            return types.SimpleNamespace(tag_name="v1.2.3")

        def get_git_ref(self, ref):
            raise Exception("lookup failed")

    install_fake_repo(monkeypatch, FakeRepo())

    assert (
        filters.get_latest_release("owner/repo", return_sha=True)
        == "LATEST_RELEASE_ERROR"
    )


@pytest.mark.parametrize(
    "branch_ref",
    [
        types.SimpleNamespace(object=git_object("tag", SHA_1)),
        types.SimpleNamespace(object=git_object("commit", "bad")),
    ],
)
def test_malformed_default_branch_sha_returns_error(monkeypatch, branch_ref):
    class FakeRepo:
        default_branch = "main"

        def get_latest_release(self):
            raise Exception("no releases")

        def get_git_ref(self, ref):
            return branch_ref

    install_fake_repo(monkeypatch, FakeRepo())

    assert (
        filters.get_latest_release("owner/repo", return_sha=True)
        == "LATEST_RELEASE_ERROR"
    )


def test_get_latest_release_error(monkeypatch):
    class FakeRepo:
        def get_latest_release(self):
            raise Exception("no releases")

    class FakeGithub:
        def __init__(self, token=None):
            pass

        def get_repo(self, name):
            raise Exception("bad repo")

    monkeypatch.setattr(filters, "Github", FakeGithub)
    filters.cache.clear()

    assert filters.get_latest_release("owner/repo") == "LATEST_RELEASE_ERROR"
