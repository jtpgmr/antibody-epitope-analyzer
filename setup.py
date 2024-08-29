from setuptools import setup, find_packages

setup(
    name="antibody-epitope-analyzer",
    version="0.0.1",
    author='Jose Luis Cruz, Jr.',
    author_email='jpgmr@gmail.com',
    description='Project that downloads epitope data from IEDB, for a given antigen, generates .fasta files containing the amino acid sequences and detects conserved regions.',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "mycommand=main:main",
        ],
    },
)