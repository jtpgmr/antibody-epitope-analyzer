from src import *

if __name__ == '__main__':
    # TODO: Add logic to download antigen epitope data files from iedb
    for file in os.listdir(epitope_data_dir):
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
