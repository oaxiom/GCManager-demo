#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
# Andrew P. Hutchins
#

import math
from . import utils
from . import html_data

def html(
    lang:str,
    patient_id:str,
    search_term:str,
    patient_data:dict,
    main_table:str,
    OR_score:float,
    ):

    # TODO: check patient data
    # TODO: check valid language
    if lang == 'EN':
        return html_en(patient_id=patient_id, search_term=search_term, patient_data=patient_data, main_table=main_table,
            OR_score=OR_score)
    elif lang == 'CN':
        return html_cn(patient_id=patient_id, search_term=search_term, patient_data=patient_data, main_table=main_table,
            OR_score=OR_score)


def html_en(
    patient_id:str,
    search_term:str,
    patient_data:dict,
    main_table:str,
    OR_score:float,
    ):
    # English version;

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
  <h1 style="text-align: right;">Disease Risk</h1>
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

<table style="width:40%">
    <tr>
        <td style="background-color: var(--tab-grey-bg);">Odds Ratio score</td>
        <td colspan="5">{OR_score:.2f}</td>
    </tr>
</table>

<p>The Odds Ratio (OR) indicates the level of risk compared to the average population. Scores greater
than 1 indicate increased risk, whilst scores less than 1 indicate a decreased risk. The magnitude of the number
represents the probability of the incidence of {search_term}, where the average incidence rate equals 1.

<hr>

<h3>Risk Alleles</h3>
<table style="width:100%">
    <tr>
        <th style="background-color: var(--tab-grey-bg);">SNP-genotype</th>
        <th style="background-color: var(--tab-grey-bg);">Gene</th>
        <th style="background-color: var(--tab-grey-bg);">Effect</th>
        <th style="background-color: var(--tab-grey-bg);" colspan="2">Risk Classification</th>
    </tr>
    {main_table}
</table>

<hr>
<h6 style='text-align:right'>Helixiome</h6>

</body>


    '''
    return html



def html_cn(
    patient_id:str,
    search_term:str,
    patient_data:dict,
    main_table:str,
    OR_score:float,
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
  <h1 style="text-align: right;">疾病风险提示</h1>
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
        <td style="background-color: var(--tab-grey-bg);">搜索术语</td>
        <td colspan="5">{search_term}</td>
    </tr>
</table>

<hr>

<h2>指导</h2>

<table style="width:40%">
    <tr>
        <td style="background-color: var(--tab-grey-bg);">OR值分 (Odds Ratio)</td>
        <td colspan="5">{OR_score:.2f}</td>
    </tr>
</table>

<p>OR值分数提示了与人群相比较的患病风险。分数大于1表示与人群相比，患病风险升高；分数小于1表示与人群相比，患病风险降低。OR值分数数值大小提示了患病风险的高低。

<hr>

<h3>风险基因分析</h3>
<table style="width:100%">
    <tr>
        <th style="background-color: var(--tab-grey-bg);">单核苷酸多态性 (SNP) 基因型</th>
        <th style="background-color: var(--tab-grey-bg);">基因</th>
        <th style="background-color: var(--tab-grey-bg);">效应</th>
        <th style="background-color: var(--tab-grey-bg);">OR值分</th>
        <th style="background-color: var(--tab-grey-bg); text-align: center" colspan="2">风险分类</th>
    </tr>
    {main_table}
</table>

<hr>

<h6 style='text-align:right'>中基科生物</h6>

</body>
    '''
    return html


