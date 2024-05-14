
# TODO: Replace with miniglbase
import os, sys, shutil
from . import tinyglbase
from . import support
from . import html_pharma

class reporter:
    def __init__(self, data_path:str, patient_id:str, patient_data:dict,
        disease_code: str, diseaseEN:str, diseaseCN:str,
        lang: str):

        # TODO: Fix the hacky language stuff
        assert lang in support.valid_laguages

        self.lang = lang
        self.patient_id = patient_id
        self.disease_code = disease_code
        if lang == 'CN':
            self.disease_name = diseaseCN
        else:
            self.disease_name = diseaseEN

        self.search_term = diseaseEN # It's always EN, for now
        self.data_path = os.path.join(data_path, f'PID.{patient_id}')
        self.patient_data = patient_data

        # make sure the css is copied over
        # Enable the if statment when you finished testing:
        #if not os.path.exists(os.path.join(data_path, f'PID.{patient_id}', 'simple.css')):
        shutil.copy(os.path.expanduser('~/static_data/html/simple.css'), os.path.join(data_path, f'PID.{patient_id}', 'simple.css'))
        shutil.copy(os.path.expanduser('~/static_data/html/print.css'), os.path.join(data_path, f'PID.{patient_id}', 'simple.css'))

    def generate(self, mode:str) -> str:
        """
        **Purpose**
            Generate a report, return the HTML filename
        """
        assert mode in support.valid_genome_dbs, f'{mode} not found'

        if mode == 'PharmaGKB':
            # TODO: Check the correct annotation file exists.
            annotated_data = self.__annotate_pharmagkb_snps(os.path.join(self.data_path, f'{self.patient_id}.pharmagkb.txt'))
            html_filename = self.__report_generator_pharmaGKB(annotated_data)

        return html_filename

    def __annotate_pharmagkb_snps(self, filename):
        '''
        **Purpose**
            This annotates the SNPs with the table;

            This is fast enough to be run each time before report generation.

            TODO: A potential bug here, as it will only consider a SNP if it's already
            annotated with vcfanno, this will only rebuild new SNPs that are correctly annotated.
            I expect it would be a tiny minority, but needs to be fixed in future versions.
        '''
        # output.write(f'{chrom}\t{rsid}\t{genotype}\n')
        pharmagkb_snps = tinyglbase.genelist(filename, format={'force_tsv': True, 'SNP': 1, 'patient_genotype': 2})

        pharmagkb = tinyglbase.glload(os.path.expanduser('~/static_data/PharmaGKB/merged_table.glb'))
        over = pharmagkb.map(genelist=pharmagkb_snps, key='SNP')

        # I need to match the genotypes, but seems the genotype and patient_genotype can be in any order when heterozygote
        results = []
        for SNP in over:
            if set(SNP['genotype']) == set(SNP['patient_genotype']):
                results.append(SNP)
        over = tinyglbase.genelist(format=True)

        over.load_list(results)

        return over

    def __report_generator_pharmaGKB(self, annotated_data):
        # TODO: Check annotated_data has phenotype and drug keys
        # TODO: remove the hacky language selecting system;

        search_results = annotated_data.getRowsByKey(key='phenotype', values=self.search_term, case_sensitive=False)
        if not search_results:
            search_results = annotated_data.getRowsByKey(key='phenotype', values=self.search_term, case_sensitive=False)

        # get the search_term

        if not search_results:
            raise AssertionError(f'No associations matching {self.search_term} were found')

        search_results.sort('drug')

        rest_of_table = []

        if not search_results:
            # TODO: Check this works: Deal with no advice situations;
            rest_of_table = '<tr><td>No relevant advice available</td><td></td><td></td><td></td></tr>'
        else:
            for drug in search_results:
                tab_row = f'''
            <tr>
                <td>{drug['drug']}</td>
                <td>{drug['SNP']}-{drug['patient_genotype']}</td>
                <td>{drug['evidence_level']}</td>
                <td>{drug['description']}</td>
            </tr>
                    '''
                rest_of_table.append(tab_row)
            rest_of_table = '\n'.join(rest_of_table)

        # TODO: Fix hacky language support
        if self.lang == 'EN':
            html = html_pharma.html('EN', self.patient_id, self.disease_name, self.patient_data, rest_of_table)
        elif self.lang == 'CN':
            html = html_pharma.html('CN', self.patient_id, self.disease_name, self.patient_data, rest_of_table)

        html_filename = os.path.join(self.data_path, f"result.{self.patient_id}.{self.lang}.{self.disease_code}.html")

        with open(html_filename, "w", encoding="utf-8", errors="xmlcharrefreplace") as output_file:
            output_file.write(html)

        return html_filename
