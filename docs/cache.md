# Cache Management

`struct` caches remote content under `~/.struct/cache` by default. Use the `--cache-policy` flag to control how cached data is used when fetching remote files:

- `always` (default): use cached content when available.
- `never`: bypass the cache and do not store fetched content.
- `refresh`: always refetch remote content and update the cache.

## Inspecting and Clearing Cache

The `cache` command lets you inspect or clear the cache:

```bash
struct cache inspect
struct cache clear
```

Use `--cache-dir` to operate on a different cache directory.
