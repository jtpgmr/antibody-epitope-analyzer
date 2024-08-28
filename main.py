from datetime import datetime as dt, timedelta as td
import json
from pytz import UTC
from zipfile import ZipFile

from src import *

# testing vars
organism='Influenza A Virus'
antigen='Hemagglutinin'
host = Host_Options.Human

if __name__ == '__main__':
    iedb_scraper = initialize_scraper()

    get_epitope_data_file(iedb_scraper, organism=organism, antigen=antigen, host=host, disease=Disease_Options.Infectious)

    epitope_data_files = os.listdir(epitope_data_dir)

    if len(epitope_data_files) == 0:
        raise Exception('No files in download directory')


    download_file_paths: List[str] = []
    for file in epitope_data_files:
        if file.startswith('epitope_table_export') and file.endswith('zip'):
            file_download_epoch = file.split('_')[-1].split('.')[0]
            file_download_epoch = dt.fromtimestamp(int(file.split('_')[-1].split('.')[0]), UTC)
            is_recent_download = (dt.now(UTC) - file_download_epoch) < td(seconds=30)

            if is_recent_download:
                zip_file_path = os.path.join(epitope_data_dir, file)
                with ZipFile(zip_file_path) as z:
                    z.extractall(epitope_data_dir)
                
                json_file_path = zip_file_path.replace('.zip', '')
                new_download_file_name = os.path.join(epitope_data_dir, f'{host_options[host].lower()}_{organism.lower().replace(" ", "_")}_{antigen.lower().replace(" ", "_")}_{dt.strftime(file_download_epoch, "%Y-%m-%d")}.json')
                os.rename(json_file_path, new_download_file_name)
                os.remove(zip_file_path)
                download_file_paths.append(new_download_file_name)

    if len(download_file_paths) > 0:
        for file in download_file_paths:
            if not file.endswith(".json"):
                continue

            with open(os.path.join(epitope_data_dir, file), 'r') as f:
                epitope_list: list[dict] = json.load(f)['Data']

            # only works for ncbi accessions
            # if not an ncbi uri, it returns '', which is then filtered out
            unique_epitope_accessions: list[str] = list(filter(
                None,
                list(set(
                    epitope['Epitope - Source Molecule IRI'].split('/protein/')[-1] if 'ncbi' in epitope['Epitope - Source Molecule IRI'] else ''
                    for epitope in epitope_list
                ))
            ))

            for accession in unique_epitope_accessions:
                request_props = construct_fasta_request_props(accession)
                generate_fasta_files(accession)
