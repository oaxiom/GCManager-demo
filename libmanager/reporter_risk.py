#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
# Andrew P. Hutchins,
#

import os, sys, shutil
from . import tinyglbase
from . import support
from . import html_risk

class reporter_risk:
    def __init__(self,
        data_path:str,
        script_path:str,
        patient_id:str,
        patient_data:dict,
        disease_code: str,
        diseaseEN:str,
        diseaseCN:str,
        log,
        lang: str):

        # TODO: Fix the hacky language stuff
        assert lang in support.valid_laguages

        self.log = log
        self.lang = lang
        self.patient_id = patient_id
        self.disease_code = disease_code
        if lang == 'CN':
            self.disease_name = diseaseCN
        else:
            self.disease_name = diseaseEN

        self.data_path = os.path.join(data_path, f'PID.{patient_id}')
        self.script_path = script_path # root for GCManager install;

        print(self.data_path, self.script_path)

        self.patient_data = patient_data

        self.search_term = diseaseEN # Hardcoded to EN, for now, should use the disease_code

        # TODO: Enable the if statment when you finished testing:
        #if not os.path.exists(os.path.join(data_path, f'PID.{patient_id}', 'simple.css')):
        # make sure the css is copied over
        shutil.copy(os.path.join(self.script_path, 'static_data', 'html', 'simple.css' ),os.path.join(data_path, f'PID.{patient_id}', 'simple.css'))
        shutil.copy(os.path.join(self.script_path, 'static_data', 'html', 'print.css' ),os.path.join(data_path, f'PID.{patient_id}', 'print.css'))

    def generate(self) -> str:
        """
        **Purpose**
            Generate a report, return the HTML filename
        """
        annotated_data = self.__annotate_risk_snps(os.path.join(self.data_path, f'{self.patient_id}.risk.txt'))

        #print(annotated_data)

        html_filename, html = self.__report_generator_Risk(annotated_data)
        return html_filename, html

    def __annotate_risk_snps(self, filename):
        '''
        **Purpose**
            This annotates the SNPs with the table;

            This is fast enough to be run each time before report generation.

            TODO: A potential bug here, as it will only consider a SNP if it's already
            annotated with vcfanno, this will only rebuild new SNPs that are correctly annotated.
            For example if a new SNP is added, it will not show up until vcfanno updates
            the annotation.
            I expect it would be a tiny minority, and very rare but needs to be fixed
            in future versions.
        '''
        risk_snps = tinyglbase.genelist(filename, format={'force_tsv': True, 'SNPS': 1, 'patient_genotype': 2})

        riskdb = tinyglbase.glload(os.path.join(self.script_path, 'static_data', 'Risk', 'risk_table.glb' ))

        # Cannot do an overlap as risk allelles don't care about het/hom.

        over = riskdb.map(genelist=risk_snps, key='SNPS')

        # I need to match the genotypes, but seems the genotype and patient_genotype can be in any order when heterozygote
        results = []
        for SNP in over:
            risk_allele = SNP['STRONGEST SNP-RISK ALLELE'].split('-')[1]
            if risk_allele in SNP['patient_genotype']:
                results.append(SNP)
        over = tinyglbase.genelist(format=True)
        over.load_list(results)

        self.log.info(f'Matched {len(over)} SNPs to GWAS Risk alleles')

        return over

    '''
        <td>单核苷酸多态性 (SNP) 基因型</td>
        <td>Gene</td>
        <td>效应</td>
        <td>Risk Classification</td>
    '''

    def __report_generator_Risk(self, annotated_data):

        # Currently searches by EN
        search_results = annotated_data.getRowsByKey(key='phenotype_EN', values=self.search_term, case_sensitive=False)

        if not search_results:
            raise AssertionError(f'No associations matching {self.search_term} were found')

        print(search_results)

        search_results.sort('risky')
        search_results.reverse()
        rest_of_table = []

        if not search_results:
            # TODO: Check this works: Deal with no advice situations;
            rest_of_table = '<tr><td>No relevant advice available</td><td></td><td></td><td></td></tr>'
        else:
            for gene in search_results:
                # do a risky score based on OR or BETA
                if '-' in gene['risky']:
                    effect = '防护的' # Protective
                elif '+' in gene['risky']:
                    effect = '有害的' # Deleterious

                tab_row = f'''
            <tr>
                <td>{gene['STRONGEST SNP-RISK ALLELE']}</td>
                <td>{gene['mapped_gene']}</td>
                <td>{effect}</td>
                <td>{gene['risky']}</td>
            </tr>
                    '''
                rest_of_table.append(tab_row)

            rest_of_table = '\n'.join(rest_of_table)

        # TODO: Fix hacky language support
        if self.lang == 'EN':
            html = html_risk.html('EN', self.patient_id, self.disease_name, self.patient_data, rest_of_table)
        elif self.lang == 'CN':
            html = html_risk.html('CN', self.patient_id, self.disease_name, self.patient_data, rest_of_table)

        html_filename = os.path.join(self.data_path, f"result.{self.patient_id}.{self.lang}.Risk.{self.disease_code}.html")

        with open(html_filename, "w", encoding="utf-8", errors="xmlcharrefreplace") as output_file:
            output_file.write(html)

        return html_filename, html
