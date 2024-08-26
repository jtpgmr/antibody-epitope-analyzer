from setuptools import setup, find_packages

setup(
    name="antibody-epitope-analyzer",
    version="0.0.1",
    author='Jose Luis Cruz, Jr.',
    author_email='jpgmr@gmail.com',
    description='Project that downloads epitope data from IEDB, for a given antigen, downloads the fasta sequence files and analyzes conserved sequences.',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "mycommand=main:main",
        ],
    },
)