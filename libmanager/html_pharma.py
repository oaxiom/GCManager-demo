#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
# Andrew P. Hutchins
#

from . import utils
from . import html_data

def html(
    lang:str,
    patient_id:str,
    search_term:str,
    patient_data:dict,
    main_table:str,
    no_reccomendation_table:str,
    summary_table:str,
    ):

    # TODO: check patient data
    # TODO: check valid language
    if lang == 'EN':
        if not no_reccomendation_table: no_reccomendation_table = '<td>None</td><td>None</td>'
        return html_en(patient_id=patient_id, search_term=search_term, patient_data=patient_data,
            main_table=main_table, no_reccomendation_table=no_reccomendation_table, summary_table=summary_table)
    elif lang == 'CN':
        if not no_reccomendation_table: no_reccomendation_table = '<td>无</td><td>无</td>'
        return html_cn(patient_id=patient_id, search_term=search_term, patient_data=patient_data,
            main_table=main_table, no_reccomendation_table=no_reccomendation_table, summary_table=summary_table)


def html_en(
    patient_id:str,
    search_term:str,
    patient_data:dict,
    main_table:str,
    no_reccomendation_table:str,
    summary_table:str,
    ):
    # English version;

    html = f'''

<!DOCTYPE html>
<html>
<head>
<style>
{html_data.style_sheet}
</style>
</head>
<body>

<div style="display: flex; justify-content: space-between;">
  <img src='{html_data.helix_logo}'>
  <h1 style="text-align: right;">Pharmacogenomics report</h1>
</div>

<hr>

<h1>Patient data</h2>

<table style="width:70%">
    <tr>
        <td style="background-color: var(--tab-grey-bg);">Patient ID</td>
        <td colspan="5">{patient_id}</td>
    </tr>
    <tr>
        <td style="background-color: var(--tab-grey-bg);">Name</td>
        <td>{utils.obfuscate_name(patient_data['name'])}</td>
        <td style="background-color: var(--tab-grey-bg);">Age</td>
        <td>{patient_data['age']}</td>
        <td style="background-color: var(--tab-grey-bg);">Sex</td>
        <td>{patient_data['sex']}</td>
    </tr>
    <tr>
        <td style="background-color: var(--tab-grey-bg);">Search Term</td>
        <td colspan="5">{search_term}</td>
    </tr>
</table>

<hr>

<h2>Guidance</h2>

<p>The following report was generated based upon sequencing data for the whole genome.
The report provides guidance on the efficacy of particular drugs, used in the treatment of
{search_term}. The table lists drugs, the specific SNP and genotype of the patient, and
provides potential guidance for treatment. The data here constitutes the best advice and
care should be taken in interpreting these results.
and best clinical practice should be followed.</p>

<hr>

<h2>Summary Table</h2>

<table style="width:100%">
    <tr>
        <th>Drug</th>
        <th>Genes</th>
        <th>Efficacy</th>
        <th>Metabolism</th>
        <th>Toxicity</th>
        <th>Medication</th>
        <th>No guidance</th>
    </tr>
    {summary_table}
</table>

<hr>

<h3>Data</h3>
<table>
    <tr>
        <th>Drug</th>
        <th>Gene</th>
        <th>SNP Genotype</th>
        <th>Effect</th>
        <th>Guidance</th>
        <th>Evidence Level</th>
    </tr>
    {main_table}
</table>

<hr>

<h3>No guidance available, treat normally</h3>
<table style="width:60%">
    <tr>
        <th>Drug</th>
        <th>Guidance</th>
    </tr>
    {no_reccomendation_table}
</table>

<h2>Drug guidance summary</h2>

<p>Note the evidence level, which indicates the evidence supporting the genetic-drug
association. Levels 1A, 1B are well supported, 2A, 2B are likely, level 3 has some supporting
evidence of an association.</p>

<hr>

<h6 style='text-align:right'>Helixiome</h6>

</body>
    '''
    return html

#############################

def html_cn(
    patient_id:str,
    search_term:str,
    patient_data:dict,
    main_table:str,
    no_reccomendation_table:str,
    summary_table:str,
    ):
    # Chinese version;

    html = f'''

<!DOCTYPE html>
<html>
<head>
<style>
{html_data.style_sheet}
</style>
</head>
<body>

<div style="display: flex; justify-content: space-between;">
  <img src='{html_data.helix_logo}'>
  <h1 style="text-align: right;">药物基因组学报告</h1>
</div>

<hr>

<h2>患者数据</h2>

<table style="width:70%">
    <tr>
        <td style="background-color: var(--tab-grey-bg);">患者 ID</td>
        <td colspan="5">{patient_id}</td>
    </tr>
    <tr>
        <td style="background-color: var(--tab-grey-bg);">姓名</td>
        <td>{utils.obfuscate_name(patient_data['name'])}</td>
        <td style="background-color: var(--tab-grey-bg);">年龄</td>
        <td>{patient_data['age']}</td>
        <td style="background-color: var(--tab-grey-bg);">性别</td>
        <td>{patient_data['sex']}</td>
    </tr>
    <tr>
        <td style="background-color: var(--tab-grey-bg);">疾病</td>
        <td colspan="5">{search_term}</td>
    </tr>
</table>

<hr>

<h2>注意</h2>

<p>以下报告是根据全基因组的测序数据生成的。该报告对用于治疗{search_term}的特定药物的疗效提供了参考。表中列出了药物、患者的特定SNP和基因型，并提供了潜在的治疗指导。
值得注意的是，这是根据数据分析形成的参考建议，在解释这些结果时应小心谨慎，并应遵循临床实践经验。</p>

<hr>

<h2>汇总表</h2>

<table style="width:100%">
    <tr>
        <th>药物</th>
        <th>基因</th>
        <th>疗效</th>
        <th>代谢</th>
        <th>毒性</th>
        <th>潜在起效剂量</th>
        <th>常规用药</th>
    </tr>
    {summary_table}
</table>

<hr>

<h3>精准用药汇总</h3>
<table>
    <tr>
        <th>药物</th>
        <th>基因</th>
        <th>单核苷酸多态性 (SNP) 基因型</th>
        <th>效应</th>
        <th>指南建议</th>
        <th>证据等级</th>
    </tr>
    {main_table}
</table>

<hr>

<h3>常规用药</h3>
<table style="width:60%">
    <tr>
        <th>药物</th>
        <th>用药建议</th>
    </tr>
    {no_reccomendation_table}
</table>

<hr>

<h2>注释</h2>

<p><b>证据等级</b>：表示支持基因与药物关联的证据，1A、1B级表示证据充分，2A、2B级表示证据可能充分，3级表示有一些支持关联的证据。</p>

<p><b>疗效</b>：具有特定基因型的患者对使用该药物治疗的反应可能会增强或减弱。
<p><b>代谢</b>：具有特定基因型的患者对该药物的代谢水平可能会增强或降低，药物在体内的清除率可能会上升或下降。
<p><b>毒性</b>：具有特定基因型的患者可能会增加或降低该药物副作用（毒性）的风险。
<p><b>潜在起效剂量</b>：具有特定基因型的患者，在该药物的使用量上，可能需要增加或减少剂量才能起效。


<hr>

<h6 style='text-align:right'>中基科生物</h6>

</body>
</html>
    '''
    return html


