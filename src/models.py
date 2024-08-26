import json
import os
import re
import requests

project_path: str = os.getcwd()
iedb_url: str = 'https://www.iedb.org/result_v3.php'

epitope_data_dir: str = os.path.join(project_path, 'iedb')
fasta_files_dir: str = os.path.join(project_path, 'fasta')
web_drivers_dir: str = os.path.join(project_path, 'drivers')

if not os.path.exists(epitope_data_dir):
    os.mkdir(epitope_data_dir)

if not os.path.exists(fasta_files_dir):
    os.mkdir(fasta_files_dir)

if not os.path.exists(web_drivers_dir):
    os.mkdir(web_drivers_dir)