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

def construct_fasta_request_props(primary_accession: str) -> dict[str]:
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
    logger.info(f'Generating fasta file for epitope primary accession "{accession}"')
    request_props = construct_fasta_request_props(accession)
    response: Response = get(**request_props)
            
    if response.status_code != 200:
        if response.status_code == 429:
            logger.warning(f'Max api call rate exceeded. Retrying file generation for epitope primary accession "{accession}"')
            # if api rate limit reached, wait a few seconds before retrying
            sleep(7.5)
            response = get(**request_props)
        else:
            logger.warning(f"Error: {response.status_code} - {response.text}")
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
        logger.debug('Web Scraping Headless')
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

    # allow page to fully load
    sleep(2.5)

    for key, value in input_props.items():
        try:
            search_field_header_div = driver.find_element(By.XPATH, f"//div[contains(text(), '{key.capitalize()}')]")

            # get the next div after the header, as it contains the input/checkbox fields
            input_div = search_field_header_div.find_element(By.XPATH, "following-sibling::div[1]")
        except NoSuchElementException:
            raise Exception(f"Field for '{key}' property not found")
        
        try:
            ui_input_autocomplete_div = input_div.find_element(By.CLASS_NAME, "autocomplete")

            ui_input_autocomplete_div.find_element(By.TAG_NAME, "input").send_keys(value)

            options = WebDriverWait(ui_input_autocomplete_div, 2).until(
                ec.presence_of_all_elements_located((By.CLASS_NAME, 'option_entry'))
            )

            # get top 3 options
            for idx, opt in enumerate(options[:3]):
                try:
                    WebDriverWait(driver, 2).until(
                        ec.element_to_be_clickable(opt)
                    ).click()
                except StaleElementReferenceException:
                    logger.info("Input options element hidden after selection. Re-fetching options.")
                    ui_input_autocomplete_div.find_element(By.TAG_NAME, "input").send_keys(value.lower())

                    options = WebDriverWait(ui_input_autocomplete_div, 2).until(
                        ec.presence_of_all_elements_located((By.CLASS_NAME, 'option_entry'))
                    )
                    
                    if idx < len(options):
                        opt = options[idx]
                        WebDriverWait(ui_input_autocomplete_div, 2).until(
                            ec.element_to_be_clickable(opt)
                        ).click()
                    else:
                        logger.info(f"Index {idx} is out of range after re-fetching options.")
        except:
            ''''''
            logger.info(f'Input box not found for "{key}". Performing alternative workflow.')

            search_field_header_div = driver.find_element(By.CLASS_NAME, f'{key}_search_box')
            search_field_value_select_area = search_field_header_div.find_element(By.CLASS_NAME, 'search_content')

            try:
                radio_btn_value = ideb_radio_buttons_options[key]
            except KeyError:
                raise Exception(f'Key not found: {key}')

            if key == 'host':
                search_field_value_field = search_field_value_select_area.find_element(By.CLASS_NAME, 'title').find_element(By.XPATH, f"//div[contains(text(), '{radio_btn_value[value] if isinstance(value, int) else value.capitalize()}')]").find_element(By.XPATH, "preceding-sibling::div[1]")
            elif key == 'disease':
                search_field_value_field = search_field_value_select_area.find_element(By.CLASS_NAME, 'title').find_element(By.XPATH, f"//div[contains(text(), '{radio_btn_value[value] if isinstance(value, int) else value.capitalize()}')]").find_element(By.XPATH, "preceding-sibling::div[1]")

            search_field_value_field.click()
    
    driver.find_element(By.CLASS_NAME, 'submitbutton').click()

    results_section_div = driver.find_element(By.CLASS_NAME, 'table_container')

    # wait for results page to load
    WebDriverWait(results_section_div, 7.5).until(
        ec.presence_of_element_located((By.CLASS_NAME, 'exportholder'))
    ).click()

    export_file_popup = driver.find_element(By.CLASS_NAME, 'inwindow_popup_content')

    # find select tag element
    select_element = WebDriverWait(export_file_popup, 2).until(
        ec.presence_of_element_located((By.XPATH, '//select[@style="float: left; margin-right: 5px;"]'))
    )

    select = Select(select_element)

    # select file format option from download popup modal
    select.select_by_value('json')

    logger.info(f"Downloading IEDB epitope export json file for {antigen} ({organism})...")
    export_file_popup.find_element(By.XPATH, '//button[@style="margin-left: 5px; margin-top: 5px;"]').click()

    # wait while file downloads
    sleep(5)

    driver.quit()

    