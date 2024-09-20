#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
# Andrew P. Hutchins,
#

import os, sys, shutil
from . import tinyglbase
from . import support
from . import html_pharma

class reporter_pharma:
    def __init__(self,
        data_path:str,
        script_path:str,
        patient_id:str,
        patient_data:dict,
        gcm_data,
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

        self.patient_data = patient_data

        self.search_term = diseaseEN # Hardcoded to EN, for now, should use the disease_code

        self.gcm_data = gcm_data

    def generate(self) -> str:
        """
        **Purpose**
            Generate a report, return the HTML filename
        """
        annotated_data, pharmagkb = self.__annotate_pharmagkb_snps(self.gcm_data.get_pharma())
        self.log.info('Annotated')
        html_filename, html = self.__report_generator_pharmaGKB(annotated_data, pharmagkb)
        self.log.info('Generated')

        return html_filename, html

    def __annotate_pharmagkb_snps(self, pharmagkb_snps):
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
        pharmagkb = tinyglbase.glload(os.path.join(self.script_path, 'static_data', 'PharmaGKB', 'pharma_table.glb' ))
        self.log.info(f'Found pharma_table {len(pharmagkb)}')
        over = pharmagkb.map(genelist=pharmagkb_snps, key='SNP')
        self.log.info(f'Mapped {len(over)}')

        # I need to match the genotypes, but seems the genotype and patient_genotype can be in any order when heterozygote
        results = []
        for SNP in over:
            if set(SNP['genotype']) == set(SNP['patient_genotype']):
                results.append(SNP)
        over = tinyglbase.genelist(format=True, log=self.log)
        over.load_list(results)

        self.log.info('Generated overlap')

        return over, pharmagkb

    def __generate_summary_table(self, no_reccomendation, summary_table_dict):
        '''
        **Purpose**


        '''
        def plus_conv(i):
            i = i.replace('+', '<span style="color: #0000aa;">⬆</span>')
            i = i.replace('-', '<span style="color: #00aa00;">⬇</span>')
            #i = i.replace(' ', '~') # if we need a ~ symbol;
            return i

        no_reccomendation_drug_names = []
        if no_reccomendation:
            no_reccomendation_drug_names = set([f"{drug['drug_CN']} ({drug['drug_EN']})" for drug in no_reccomendation])

        rowspans = {}
        for drug in sorted(list(summary_table_dict.keys()) + list(no_reccomendation_drug_names)):
            if drug in no_reccomendation_drug_names:
                rowspans[drug] = 1
            else:
                rowspans[drug] = len(summary_table_dict[drug].keys())

        summary_table = []
        for drug in sorted(list(summary_table_dict.keys()) + list(no_reccomendation_drug_names)):
            if drug in no_reccomendation_drug_names:
                tab_row = f'''
                <tr>
                    <td>{drug}</td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td>✔</td> <!-- normal medication -->
                </tr>
                '''
                summary_table.append(tab_row.replace('  ', ''))

            else: # In the summary_table_dict:
                for rid, gene in enumerate(sorted(list(summary_table_dict[drug].keys()))):

                    advice_data = summary_table_dict[drug][gene]
                    advice_row = f'''
                        <td>{plus_conv(advice_data["疗效"])}</td>
                        <td>{plus_conv(advice_data["代谢"])}</td>
                        <td>{plus_conv(advice_data["毒性"])}</td>
                        <td>{plus_conv(advice_data["剂量"])}</td>
                        <td></td>
                        '''

                    if rid == 0: #
                        tab_row = f'''
                        <tr>
                        <td rowspan="{rowspans[drug]}">{drug}</td>
                        <td><i>{gene}</i></td>
                        {advice_row}
                        </tr>
                        '''
                    else:
                        tab_row = f'''
                        <tr>
                        <!-- skip -->
                        <td><i>{gene}</i></td>
                        {advice_row}
                        </tr>
                        '''

                    summary_table.append(tab_row.replace('  ', ''))

        return '\n'.join(summary_table)

    def __report_generator_pharmaGKB(self, annotated_data, pharmagkb):
        # TODO: Check annotated_data has phenotype and drug keys
        # TODO: remove the hacky language selecting system;
        # TODO: Do it the other way around, search for drug, get phenotypes.
        # TODO: Split this huge function up into sub functions;

        # Currently searches by EN
        search_results = annotated_data.getRowsByKey(key='phenotype_EN', values=self.search_term, case_sensitive=False)
        #if not search_results:
        #    search_results = annotated_data.getRowsByKey(key='drug', values=self.search_term, case_sensitive=False)

        # Get the ones with no recommendation
        # First, get all phenotype from the pharmagkb database:
        # Second, if it's in the search_results, remove it;
        pharmagkb_all_this_phenotype = pharmagkb.getRowsByKey(key='phenotype_EN', values=self.search_term, case_sensitive=False)

        if not search_results:
            # There was no adivce
            no_reccomendation = pharmagkb_all_this_phenotype
            no_reccomendation = no_reccomendation.removeDuplicates('drug_CN')
            no_reccomendation.sort('drug_CN')
        else:
            no_reccomendation = search_results.map(genelist=pharmagkb_all_this_phenotype, key='drug_CN', logic='notright')
            if no_reccomendation:
                no_reccomendation = no_reccomendation.removeDuplicates('drug_CN')
                no_reccomendation.sort('drug_CN')
            search_results.sort('drug_CN')

        #if not search_results:
        #    raise AssertionError(f'No associations matching {self.search_term} were found')

        rest_of_table = []
        no_reccomendation_table = []

        if self.lang == 'EN':
            no_rec = 'No guidance'
        else:
            no_rec = '常规用药'

        if not search_results:
            if self.lang == 'EN':
                rest_of_table = '<tr><td>None</td><td>None</td><td>None</td><td>None</td><td>None</td><td>None</td></tr>'
            else:
                rest_of_table = '<tr><td>无</td><td>无</td><td>无</td><td>无</td><td>无</td><td>无</td></tr>'
        else:
            for drug in search_results:
                if self.lang == 'EN':
                    SNP_impact = drug['SNP_impact_EN']
                    description = drug['description_EN']
                else:
                    SNP_impact = drug['SNP_impact_CN']
                    description = drug['description_CN']

                tab_row = f'''
            <tr>
                <td>{drug['drug_CN']}<br>({drug['drug_EN']})</td>
                <td>{drug['gene']}</td>
                <td>{drug['SNP']}-{drug['patient_genotype']}</td>
                <td>{SNP_impact}</td>
                <td>{description}</td>
                <td>{drug['evidence_level']}</td>
            </tr>
                    '''
                rest_of_table.append(tab_row.replace('  ', ''))
            rest_of_table = '\n'.join(rest_of_table)

        if no_reccomendation:
            for drug in no_reccomendation:
                tab_row_no_rec = f'''
                    <tr>
                    <td>{drug['drug_CN']} ({drug['drug_EN']})</td>
                    <td>{no_rec}</td>
                    </tr>
                '''
                no_reccomendation_table.append(tab_row_no_rec.replace('  ', ''))
            no_reccomendation_table = '\n'.join(no_reccomendation_table)

        # THe summary top table
        summary_table_dict = {}
        # Summary table:
        # 1. Drug 2. Genes 3. 疗效 (Efficacy)  4. 代谢 (Metabolism)  5.  风险 (Risk) ...
        if search_results:
            for drug in search_results:
                drug_name = f"{drug['drug_CN']} ({drug['drug_EN']})"
                if drug_name not in summary_table_dict:
                    summary_table_dict[drug_name] = {}
                if drug['gene'] not in summary_table_dict[drug_name]:
                    summary_table_dict[drug_name][drug['gene']] = {'疗效': '', '代谢': '', '风险': '', '毒性': '', '剂量': ''}

                for impacts in drug['SNP_impact_CN'].replace('/', ';').split(';'):
                    if impacts == '其他':
                        continue
                    elif impacts == '药物动力学': # Pharmacokinetics;
                        continue
                    inc_dec = drug['inc_dec']
                    summary_table_dict[drug_name][drug['gene']][impacts] += inc_dec

        # convert the summary_table to HTML:
        summary_table = self.__generate_summary_table(no_reccomendation, summary_table_dict)

        html = ''

        # TODO: Fix hacky language support
        if self.lang == 'EN':
            html = html_pharma.html('EN', self.patient_id, self.disease_name, self.patient_data, rest_of_table, no_reccomendation_table, summary_table)
        elif self.lang == 'CN':
            html = html_pharma.html('CN', self.patient_id, self.disease_name, self.patient_data, rest_of_table, no_reccomendation_table, summary_table)

        html_filename = os.path.join(self.data_path, f"result.{self.patient_id}.{self.lang}.Pharma.{self.disease_code}.html")

        with open(html_filename, "w", encoding="utf-8", errors="xmlcharrefreplace") as output_file:
            output_file.write(html)

        return html_filename, html
