from setuptools import setup, find_packages

# TODO package data

with open('README.md', 'r') as fh:
    long_description = fh.read()

print('FIND PACKAGES OUTPUT:', find_packages())


setup(
    name='bddl',
    version='0.0.4',
    author='Stanford University',
    long_description_content_type='text/markdown',
    long_description=long_description,
    url='https://github.com/StanfordVL/bddl',
    zip_safe=False,
    packages=find_packages(),
    install_requires=[
        'pytest',
        'numpy',
        'networkx',
        'jupytext'
    ],
    package_data={},
    include_package_data=True
)
