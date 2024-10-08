import inspect
import os
from requests import get, Response
from time import sleep
from typing import List, Union

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.driver_cache import DriverCacheManager

from src.models import *

def get_antigen_uniprot_id(antigen_name: str) -> str:
    ''''''

def construct_fasta_request_props(primary_accession: str) -> dict:
    """
        Construct request to NCBI website, to retrive fasta data for a given `primary_accession`

        :param primary_accession: the main, unique identifier assigned to a biological sequence or record in a database, generated from experimentally-derived data
        :return: request params for the `requests` library
    """

    params = {
        "db": "protein",
        "id": primary_accession,
        "rettype": "fasta",
        "retmode": "text"
    }

    return {
        "url": fasta_source_url,
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


def initialize_scraper(headless: bool = False) -> webdriver.Chrome:
    ''''''
    options: webdriver.ChromeOptions = Options()

    if headless:
        options.add_argument('--headless')
        logging.debug('Web Scraping Headless')
    else:
        options.add_argument('start-maximized')

    options.add_experimental_option('prefs', { 'download.default_directory': epitope_data_dir })

    try:
        cache_manager = DriverCacheManager(web_drivers_dir)
        service = Service(ChromeDriverManager(cache_manager=cache_manager).install())
    except:
        raise Exception('Issue applying chrome driver binaries')

    try:
        driver = webdriver.Chrome(service=service, options=options)
    except:
        raise Exception('Scraper failed to initialize')

    return driver

def get_epitope_data_file(driver: webdriver.Chrome, organism: str, antigen: str, host: Union[str, int] = None, disease: Union[str, int] = None, **kwargs):
    ''''''
    # get optional input props (used as querying params on the iedb website)
    frame = inspect.currentframe()
    args, _, _, values = inspect.getargvalues(frame)
    input_props: dict[str, Union[str| int | None]] = {arg: values[arg] for arg in args if values[arg] is not None and isinstance(values[arg], Union[str, int] )}

    driver.get(antigen_epitopes_url)

    for key, value in input_props.items():
        try:
            search_field_header_div = driver.find_element(By.XPATH, f"//div[contains(text(), '{key.capitalize()}')]")

            # get the next div after the header, as it contains the input/checkbox fields
            value_div = search_field_header_div.find_element(By.XPATH, "following-sibling::div[1]")
        except NoSuchElementException:
            raise Exception(f"Field for '{key}' property not found")
        
        try:
            Ui_input_autocomplete_div = value_div.find_element(By.CLASS_NAME, "autocomplete")

            Ui_input_autocomplete_div.find_element(By.TAG_NAME, "input").send_keys(value)

            options = WebDriverWait(Ui_input_autocomplete_div, 3).until(
                ec.presence_of_all_elements_located((By.CLASS_NAME, 'option_entry'))
            )

            # get top 3 options
            for idx, opt in enumerate(options[:3]):
                try:
                    WebDriverWait(driver, 3).until(
                        ec.element_to_be_clickable(opt)
                    ).click()
                except StaleElementReferenceException:
                    print("Input options element hidden after selection. Re-fetching options.")
                    Ui_input_autocomplete_div.find_element(By.TAG_NAME, "input").send_keys(value.lower())

                    options = WebDriverWait(Ui_input_autocomplete_div, 3).until(
                        ec.presence_of_all_elements_located((By.CLASS_NAME, 'option_entry'))
                    )
                    
                    if idx < len(options):
                        opt = options[idx]
                        WebDriverWait(Ui_input_autocomplete_div, 3).until(
                            ec.element_to_be_clickable(opt)
                        ).click()
                    else:
                        print(f"Index {idx} is out of range after re-fetching options.")
        except:
            ''''''
            logging.info("Input box not found. Performing alternative workflow")

            search_field_header_div = driver.find_element(By.CLASS_NAME, f'{key}_search_box')
            search_field_value_select_area = search_field_header_div.find_element(By.CLASS_NAME, 'search_content')

            if key == 'host':
                ''''''
                search_field_value_field = search_field_value_select_area.find_element(By.CLASS_NAME, 'title').find_element(By.XPATH, f"//div[contains(text(), '{host_options[value]}')]").find_element(By.XPATH, "preceding-sibling::div[1]")
            elif key == 'disease':
                ''''''
                search_field_value_field = search_field_value_select_area.find_element(By.CLASS_NAME, 'title').find_element(By.XPATH, f"//div[contains(text(), '{disease_options[value]}')]").find_element(By.XPATH, "preceding-sibling::div[1]")
            else:
                raise Exception(f'Key not found: {key}')

            search_field_value_field.click()
    
    driver.find_element(By.CLASS_NAME, 'submitbutton').click()

    # wait for results page to load
    WebDriverWait(driver, 5).until(
        ec.presence_of_element_located((By.CLASS_NAME, 'exportholder'))
    ).click()

    export_file_popup = driver.find_element(By.CLASS_NAME, 'inwindow_popup_content')

    # find select tag element
    select_element = WebDriverWait(export_file_popup, 3).until(
        ec.presence_of_element_located((By.XPATH, '//select[@style="float: left; margin-right: 5px;"]'))
    )

    select = Select(select_element)

    # select file format option from download popup modal
    select.select_by_value('json')

    WebDriverWait(export_file_popup, 6).until(
        ec.visibility_of_element_located((By.XPATH, '//button[@style="margin-left: 5px; margin-top: 5px;"]'))
    ).click()

    # wait while file downloads
    sleep(5)

    driver.quit()

    