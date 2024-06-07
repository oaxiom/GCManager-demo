
from . import html_data

def html(
    lang:str,
    patient_id:str,
    search_term:str,
    patient_data:dict,
    main_table:str,
    judgement:str,
    factor:str,
    ):

    # TODO: check patient data
    # TODO: check valid language
    if lang == 'EN':
        1/0 # Not implemented;
        #if not no_reccomendation_table: no_reccomendation_table = '<td>None</td><td>None</td>'
        #return html_en(patient_id=patient_id, search_term=search_term, patient_data=patient_data, main_table=main_table)
    elif lang == 'CN':
        return html_cn(patient_id=patient_id, search_term=search_term, patient_data=patient_data, main_table=main_table,
            judgement=judgement, factor=factor)


def html_en(
    patient_id:str,
    search_term:str,
    patient_data:dict,
    main_table:str,
    judgement:str,
    factor:str,
    ):
    # English version;

    html = f'''


    '''
    return html



def html_cn(
    patient_id:str,
    search_term:str,
    patient_data:dict,
    main_table:str,
    judgement:str,
    factor:str,
    ):
    # Chinese version;

    html = f'''

<!DOCTYPE html>
<html>
<head>
<style>
{html_data.style_sheet}
{html_data.rounded_rects_styles}
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
        <td>{patient_data['name']}</td>
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

<h3>精准用药汇总</h3>
<table style="width:100%">
    <tr>
        <th style="background-color: var(--tab-grey-bg);">单核苷酸多态性 (SNP) 基因型</th>
        <th style="background-color: var(--tab-grey-bg);">基因</th>
        <th style="background-color: var(--tab-grey-bg);">效应</th>
        <th style="background-color: var(--tab-grey-bg);" colspan="2">风险分类</th>
    </tr>
    {main_table}
</table>

<hr>

<h6 style='text-align:right'>中基科生物</h6>

</body>
    '''
    return html


