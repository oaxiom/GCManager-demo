

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

    # As can't escape {} in f string?
    div_style = '''
    .rounded-rectangleL {
    width: 200px;
    height: 15px;
    background-color: #FFFFFF;
    border-radius: 2px;
    }
    .rounded-rectangleR {
    right: 0px;
    width: 200px;
    height: 15px;
    background-color: #FFFFFF;
    border-radius: 2px;
    }
    '''

    html = f'''

<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" media="screen" href="simple.css">
<link rel="stylesheet" media="print" href="print.css">
<style>
{div_style}
</style>
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

<!--
<h2>指导</h2>
<table style="width:50%">
    <tr>
        <td>总体风险/Overall Risk</td>
        <td>{judgement}</td>
    </tr>
    <tr>
        <td>风险评分</td>
        <td>{factor}</td>
    </tr>
</table>
-->




<h3>精准用药汇总</h3>
<table>
    <tr>
        <th>单核苷酸多态性 (SNP) 基因型</th>
        <th>基因</th>
        <th>效应</th>
        <th colspan="2">风险分类</th>
    </tr>
    {main_table}
</table>


<h3>报告生成者中基科</h3>

</body>
    '''
    return html


