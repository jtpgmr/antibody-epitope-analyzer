import os
from requests import get, Response
from time import sleep
import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.driver_cache import DriverCacheManager

from src.models import *

def get_antigen_uniprot_id(antigen_name: str) -> str:
    ''''''

def construct_fasta_request_props(accession: str):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    params = {
        "db": "protein",
        "id": accession,
        "rettype": "fasta",
        "retmode": "text"
    }

    return {
        "url": url,
        "params": params
    }

def generate_fasta_files(accession: str) -> None:
    request_props = construct_fasta_request_props(accession)
    response: Response = get(**request_props)
            
    if response.status_code != 200:
        if response.status_code == 429:
            # if api rate limit reached, wait a few seconds before retrying
            sleep(7.5)
            response = get(**request_props)
        else:
            print(f"Error: {response.status_code} - {response.text}")
            raise 
    
    sequence = response.text.split('\n')[1:]
    sequence = '\n'.join(sequence)

    with open(os.path.join(fasta_files_dir, f"{accession}.fasta"), 'w') as f:
        f.write(sequence)


def initialize_scraper(headless: bool = False, install_latest_driver: bool = False) -> webdriver:
    ''''''
    options: webdriver.ChromeOptions = Options()

    if headless:
        options.add_argument('--headless')
        logging.debug('Web Scraping Headless')
    else:
        options.add_argument('start-maximized')

    options.add_experimental_option(
        'prefs',
        {
            'download.default_directory': epitope_data_dir
        }
    )

    web_drivers_dir_content = os.listdir(web_drivers_dir)
    service: Service

    try:
        if len(web_drivers_dir_content) == 0 or install_latest_driver == True:
            service = Service(ChromeDriverManager().install())
        else:
            cache_manager = DriverCacheManager(web_drivers_dir)
            service = Service(ChromeDriverManager(cache_manager=cache_manager).install())
    except:
        raise Exception('Issue applying chrome driver binaries')


    try:
        driver = webdriver.Chrome(service=service)
    except:
        raise Exception('Scraper failed to initialize')

    return driver

def get_epitope_data_file(driver: webdriver, organism: str, antigen: str, host_species: str, disease_type: str):
    ''''''