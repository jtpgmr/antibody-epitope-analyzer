import json
import os
import re
import requests

project_path: str = os.getcwd()
antigen_epitopes_url: str = 'https://www.iedb.org/result_v3.php'
fasta_source_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

epitope_data_dir: str = os.path.join(project_path, 'iedb')
fasta_files_dir: str = os.path.join(project_path, 'fasta')
web_drivers_dir: str = os.path.join(project_path, 'drivers')

if not os.path.exists(epitope_data_dir):
    os.mkdir(epitope_data_dir)

if not os.path.exists(fasta_files_dir):
    os.mkdir(fasta_files_dir)

if not os.path.exists(web_drivers_dir):
    os.mkdir(web_drivers_dir)


host_options = {
    1: "Any",
    2: "Human",
    3: "Mouse",
    4: "Non-human primate",
    5: None
}

class Host_Options:
    Any = 1
    Human = 2
    Mouse = 3
    Non_human_primate = 4
    N_a = 5

disease_options = {
    1: "Any",
    2: "Infectious",
    3: "Allergic",
    4: "Autoimmune",
    5: "Transplant",
    6: "Cancer",
    7: "None (Healthy)",
    8: None
}

class Disease_Options:
    Any = 1
    Infectious = 2
    Allergic = 3
    Autoimmune = 4
    Transplant = 5
    Cancer = 6
    Healthy = 7
    N_a = 8
