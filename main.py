from datetime import datetime as dt, timedelta as td
import glob
import json
from pytz import UTC
from zipfile import ZipFile

from src import *

# testing vars
organism='Influenza A Virus'
antigen='Hemagglutinin'
host: Union[str|int] = IEDBRadioButtonOptions.HostOptions.Human
disease: Union[str|int] = IEDBRadioButtonOptions.DiseaseOptions.Infectious

if __name__ == '__main__':
    skip = False
    if not skip:
        iedb_scraper = initialize_scraper()

        get_epitope_data_file(iedb_scraper, organism=organism, antigen=antigen, host=host, disease=disease)

        epitope_data_files = os.listdir(epitope_data_dir)

        if len(epitope_data_files) == 0:
            raise Exception('No files in download directory')

        download_files_path: List[str] = []
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
                    new_download_file_name = os.path.join(epitope_data_dir, f'{ideb_radio_buttons_options["host"][host] if isinstance(host, int) else host.capitalize()}_{organism.lower().replace(" ", "_")}_{antigen.lower().replace(" ", "_")}_{dt.strftime(file_download_epoch, "%Y-%m-%d")}.json')
                    os.rename(json_file_path, new_download_file_name)
                    os.remove(zip_file_path)
                    download_files_path.append(new_download_file_name)

        if len(download_files_path) > 0:
            for file in download_files_path:
                if not file.endswith(".json"):
                    continue

                with open(os.path.join(epitope_data_dir, file), 'r') as f:
                    epitope_list: list[dict[str]] = json.load(f)['Data']

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
                    generate_fasta_files(accession)
    
    fasta_files = glob.glob(os.path.join(fasta_files_dir, '*.fasta'))
    print(fasta_files)