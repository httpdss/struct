from setuptools import setup, find_packages

def parse_requirements(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    return [line.strip() for line in lines if line and not line.startswith('#')]

setup(
    name='struct',
    version='1.0.0',
    packages=find_packages(),
    install_requires=parse_requirements('requirements.txt'),
    entry_points={
        'console_scripts': [
            'struct = struct_module.main:main',
        ],
    },
    include_package_data=True,
    package_data={
      '': ['contribs/*'],
    },
)
