

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

<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" media="screen" href="simple.css">
<link rel="stylesheet" media="print" href="print.css">
</head>
<body>

<h1>Pharmacogenomics report</h1>

<h1>Patient data</h2>

<table style="width:50%">
    <tr>
        <td>Patient ID</td>
        <td>{patient_id}</td>
    </tr>
    <tr>
        <td>Name</td>
        <td>{patient_data['name']}</td>
    </tr>
    <tr>
        <td>Age</td>
        <td>{patient_data['age']}</td>
    </tr>
    <tr>
        <td>Sex</td>
        <td>{patient_data['sex']}</td>
    </tr>
    <tr>
        <td>Search Term</td>
        <td>{search_term}</td>
    </tr>
</table>

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
    {main_table}
</table>

<br>No guidance available, treat normally.
<table style="width:60%">
    <tr>
        <td>Drug</td>
        <td>Guidance</td>
    </tr>
    {no_reccomendation_table}
</table>

<h2>Post script</h2>
<p>Generated by Helixiome.</p>

</body>
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
<link rel="stylesheet" media="screen" href="simple.css">
<link rel="stylesheet" media="print" href="print.css">
</head>
<body>

<h1>疾病风险提示</h1>

<h1>患者数据</h2>

<table style="width:50%">
    <tr>
        <td>患者 ID</td>
        <td>{patient_id}</td>
    </tr>
    <tr>
        <td>姓名</td>
        <td>{patient_data['name']}</td>
    </tr>
    <tr>
        <td>年龄</td>
        <td>{patient_data['age']}</td>
    </tr>
    <tr>
        <td>性别</td>
        <td>{patient_data['sex']}</td>
    </tr>
    <tr>
        <td>Search Term</td>
        <td>{search_term}</td>
    </tr>
</table>

<h2>指导</h2>

<table style="width:50%">
    <tr>
        <td>总体风险/Overall Risk</td>
        <td>{judgement}</td>
    </tr>
    <tr>
        <td>风险评分/Risk score</td>
        <td>{factor}</td>
    </tr>
</table>

<h3>精准用药汇总</h3>
<table>
    <tr>
        <td>单核苷酸多态性 (SNP) 基因型</td>
        <td>基因</td>
        <td>效应</td>
        <td>风险分类/Risk Classification</td>
    </tr>
    {main_table}
</table>

<h3>报告生成者中基科</h3>

</body>
    '''
    return html


