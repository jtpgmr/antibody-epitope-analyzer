import logging
import os

set_env = os.getenv('ENV')
env = set_env if set_env else 'PROD'

get_project_path = os.getenv('PROJECT_PATH')
project_path: str = get_project_path if get_project_path else os.getcwd()
display_all_logs = os.getenv('DISPLAY_ALL_LOGS')

tmp_dir = os.path.join(project_path, 'tmp')
epitope_data_dir: str = os.path.join(tmp_dir, 'iedb')
fasta_files_dir: str = os.path.join(tmp_dir, 'fasta')
web_drivers_dir: str = os.path.join(tmp_dir, 'drivers')


if env == 'DEV':
    logging_dir = os.path.join(project_path, '.logs')
    logging_file = os.path.join(logging_dir, 'log.log')

    if not os.path.exists(logging_dir):
        os.mkdir(logging_dir)
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S',
        filename=logging_file,
        filemode='w'
    )

else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S',
    )

if not display_all_logs or display_all_logs.lower() == 'false':
    logging.getLogger('WDM').setLevel(logging.WARNING) 
    logging.getLogger('selenium.webdriver').setLevel(logging.WARNING) 
    logging.getLogger('urllib3').setLevel(logging.WARNING)


project_name = os.path.split(project_path)[-1]
logger_name = f'{project_name}-{env}' if env != 'PROD' else project_name

logger: logging.Logger = logging.getLogger(logger_name)

antigen_epitopes_url: str = 'https://www.iedb.org/result_v3.php'
fasta_source_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

if not os.path.exists(tmp_dir):
    os.mkdir(tmp_dir)

if not os.path.exists(epitope_data_dir):
    os.mkdir(epitope_data_dir)

if not os.path.exists(fasta_files_dir):
    os.mkdir(fasta_files_dir)

if not os.path.exists(web_drivers_dir):
    os.mkdir(web_drivers_dir)


ideb_radio_buttons_options = {
    "host": {
        1: "Any",
        2: "Human",
        3: "Mouse",
        4: "Non-human primate",
        5: "specified"
    },
    "disease": {
        1: "Any",
        2: "Infectious",
        3: "Allergic",
        4: "Autoimmune",
        5: "Transplant",
        6: "Cancer",
        7: "None (Healthy)",
        8: None
    }
}

class IEDBRadioButtonOptions:
    class HostOptions:
        Any = 1
        Human = 2
        Mouse = 3
        Non_human_primate = 4
        N_a = 5

    class DiseaseOptions:
        Any = 1
        Infectious = 2
        Allergic = 3
        Autoimmune = 4
        Transplant = 5
        Cancer = 6
        Healthy = 7
        N_a = 8
    