from Bio import AlignIO, SeqIO
from pytz import UTC
from zipfile import ZipFile

from src import *

# testing vars
organism='Influenza A Virus'
antigen='Hemagglutinin'
host: Union[str|int] = IEDBRadioButtonOptions.HostOptions.Human
disease: Union[str|int] = IEDBRadioButtonOptions.DiseaseOptions.Infectious



if __name__ == '__main__':
    skip = True
    if not skip:
        iedb_scraper = initialize_scraper()

        scrape_epitope_data_file(iedb_scraper, organism=organism, antigen=antigen, host=host, disease=disease)

        epitope_data_file = glob.glob(os.path.join(epitope_data_dir, 'epitope_table_export*.zip'))

        if len(epitope_data_file) == 0:
            raise Exception('No files in download directory')

        utc_now = dt.now(UTC)
        download_files_path: List[str] = []
        for file in epitope_data_file:
            file_download_epoch = file.split('_')[-1].split('.')[0]
            file_download_epoch = dt.fromtimestamp(int(file.split('_')[-1].split('.')[0]), UTC)
            is_recent_download = (utc_now - file_download_epoch) < td(seconds=30)

            if is_recent_download:
                zip_file_path = os.path.join(epitope_data_dir, file)
                with ZipFile(zip_file_path) as z:
                    z.extractall(epitope_data_dir)
                
                json_file_path = zip_file_path.replace('.zip', '')
                new_download_file_name = os.path.join(epitope_data_dir, f'{ideb_radio_buttons_options["host"][host].lower() if isinstance(host, int) else host.lower()}_{organism.lower().replace(" ", "_")}_{antigen.lower().replace(" ", "_")}_{dt.strftime(file_download_epoch, "%Y-%m-%d")}_epitopes.json')
                os.rename(json_file_path, new_download_file_name)
                os.remove(zip_file_path)
                download_files_path.append(new_download_file_name)

        if len(download_files_path) > 0:
            for file in download_files_path:
                if (
                    not file.endswith(".json") or ## check file type
                    not os.path.split(file)[-1].startswith(ideb_radio_buttons_options["host"][host].lower() if isinstance(host, int) else host.lower()) or # check start of file name
                    not utc_now.strftime('%Y-%m-%d') in file # check date of download
                ):
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

                [scrape_fasta_data(fasta_source_url, accession) for accession in unique_epitope_accessions]
        else:
            raise Exception('No fasta files have been downloaded.')

                    
    combined_fasta_file = os.path.join(muscle_fasta_files_dir, 'unaligned.fasta')
    with open(combined_fasta_file, 'w') as f:
        for file in glob.glob(os.path.join(scraped_fasta_files_dir, '*.fasta')):
            logger.info(f"Processing file: {file}")
            for record in SeqIO.parse(file, "fasta"):
                logger.info(f"Writing record: {record.id}, Length: {len(record.seq)}")
                SeqIO.write(record, f, "fasta")

    aligned_data_file = os.path.join(muscle_fasta_files_dir, 'aligned.fasta')
    command_output = exec_muscle_command(combined_fasta_file, aligned_data_file)

    with open(os.path.join(muscle_fasta_files_dir, 'command_output.txt'), 'w') as f:
        f.write(command_output)

    aligned_data = AlignIO.read(aligned_data_file, 'fasta')


    for record in aligned_data:
        print(f"Sequence ID: {record.id}")
        print(f"Sequence: {record.seq}")
        print(f"\n\n")