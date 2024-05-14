
# TODO: Replace with miniglbase
import os, sys, shutil
from . import tinyglbase
from . import support

class reporter:
    def __init__(self, data_path:str, patient_id:str, disease_code: str, lang: str):
        assert lang in support.valid_laguages

        self.lang = lang
        self.patient_id = patient_id
        self.disease_code = disease_code
        self.data_path = os.path.join(data_path, f'PID.{patient_id}')

        # make sure the css is copied over
        # Enable when you finished testing:
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
            html_filename = self.__report_generator_pharmaGKB(annotated_data, self.disease_code)

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

    def __report_generator_pharmaGKB(self, annotated_data, phenotype:str=None, drug:str=None):
        # TODO: Check annotated_data has phenotype and drug keys

        search_term = None
        if phenotype and drug:
            # TODO: Perhaps
            raise AssertionError('Cannot use phenotype and drug together')
        elif phenotype:
            search_term = phenotype
            search_results = annotated_data.getRowsByKey(key='phenotype', values=search_term, case_sensitive=False)
        elif drug:
            search_term = drug
            search_results = annotated_data.getRowsByKey(key='drug', values=search_term, case_sensitive=False)

        # get the search_term

        if len(search_results) == 0:
            raise AssertionError(f'No associations matching {search_term} were found')

        search_results.sort('drug')

        rest_of_table = []

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
            html = self.__html_en(search_term, rest_of_table)
        elif self.lang == 'CN':
            html = self.__html_cn(search_term, rest_of_table)

        filename_safe_search_term = search_term.replace(',', '').replace(' ', '_').replace(':', '_').replace('/', '_').replace('\\', '_')

        html_filename = os.path.join(self.data_path, f"result.{self.patient_id}.{filename_safe_search_term}.html")

        with open(html_filename, "w", encoding="utf-8", errors="xmlcharrefreplace") as output_file:
            output_file.write(html)

        return html_filename

    #TODO: Shift these into other python module and make generic
    def __html_en(self, search_term:str, rest_of_table:str):

        html = f'''

<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" media="screen" href="simple.css">
<link rel="stylesheet" media="print" href="print.css">
</head>
<body>

<h1>Pharmacogenomics report</h1>

<h1>Patient data</h2>

<p>Patient ID: {self.patient_id}
<br>Search Term: {search_term}</p>

<h2>Guidance</h2>

<p>The following report was generated based upon sequencing data for the whole genome.
The report provides guidance on the efficacy of particular drugs, used in the treatment of
{search_term}. The table lists drugs, the specific SNP and genotype of the patient, and
provides potential guidance for treatment. The data here constitutes the best advice and
care should be taken in interpreting these results.
and best clinical practice should be followed.</p>

<h2>Drug guidance summary</h2>

<p>Note the evidence level, which indicates the evidence supporting the genetic-drug
association. Levels 1A, 1B are well supported, 2A, 2B are likely, level 3 has some supporting
evidence of an association.</p>

<table>
    <tr>
        <td>Drug</td>
        <td>SNP Genotype</td>
        <td>Evidence Level</td>
        <td>Guidance</td>
    </tr>
    {rest_of_table}
</table>

<h2>Post script</h2>
<p>Generated by Helixiome.</p>

</body>
        '''
        return html



    def __html_cn(self, search_term, rest_of_table):

        html = f'''
<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="simple.css">
</head>
<body>

<h1>Pharmacogenomics report</h1>

<h1>Patient data</h2>

<p>Patient ID: {self.patient_id}
<br>Search Term: {search_term}</p>

<h2>Guidance</h2>

<p>以下报告是根据整个基因组的测序数据生成的。
该报告为用于治疗的特定药物的疗效提供了指导
{search_term}。该表列出了药物、患者的特定SNP和基因型，以及
为治疗提供了潜在的指导。此处的数据构成了最佳建议和
在解释这些结果时应小心谨慎。
并应遵循最佳临床实践。</p>

<h2>Drug guidance summary</h2>

<p>注意证据水平，表明支持遗传药物的证据
协会1A、1B级得到很好的支持，2A、2B级可能得到支持，3级有一些支持
关联的证据。</p>

<table>
    <tr>
        <td>Drug</td>
        <td>SNP Genotype</td>
        <td>Evidence Level</td>
        <td>Guidance</td>
    </tr>
    {rest_of_table}
</table>

<h2>Post script</h2>
<p>Generated by Helixiome.</p>

</body>
        '''
        return html
