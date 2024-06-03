

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

<h2>Summary Table</h2>

<table style="width:100%">
    <tr>
        <td>Drug</td>
        <td>Genes</td>
        <td>Efficacy</td>
        <td>Metabolism</td>
        <td>Risk</td>
        <td>Toxicity</td>
    </tr>
    {summary_table}
</table>

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
    no_reccomendation_table:str,
    summary_table:str,
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

<h1>药物基因组学报告</h1>

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
        <td>疾病</td>
        <td>{search_term}</td>
    </tr>
</table>

<h2>声明</h2>

<p>以下报告是根据整个基因组的测序数据生成的。
该报告为用于治疗的特定药物的疗效提供了指导
{search_term}。该表列出了药物、患者的特定SNP和基因型，以及
为治疗提供了潜在的指导。此处的数据构成了最佳建议和
在解释这些结果时应小心谨慎。
并应遵循最佳临床实践。</p>

<h2>Summary Table</h2>

<table style="width:100%">
    <tr>
        <td>药物</td>
        <td>基因</td>
        <td>疗效</td>
        <td>代谢</td>
        <td>风险</td>
        <td>常规用药</td>
    </tr>
    {summary_table}
</table>

<h3>精准用药汇总</h3>
<table>
    <tr>
        <td>药物</td>
        <td>基因</td>
        <td>单核苷酸多态性 (SNP) 基因型</td>
        <td>效应</td>
        <td>指南建议</td>
        <td>证据等级</td>
    </tr>
    {main_table}
</table>

<h3>常规用药</h3>
<table style="width:60%">
    <tr>
        <td>药物</td>
        <td>Guidance</td>
    </tr>
    {no_reccomendation_table}
</table>

<h2>注意</h2>

<p>注意：证据水平等级，表明支持遗传药物的证据 协会，1A、1B级表示得到很好的支持，2A、2B级可能得到支持，3级有一些支持关联的证据。</p>

<h3 style='text-align:center'>中基科生物</h3>

</body>
</html>
    '''
    return html


