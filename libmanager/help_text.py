#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):

from . import html_data

########################################################
# Doctorend Help CN
########################################################

doctor_help_text_cn = f'''

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
  <h1 style="text-align: right;">帮助文档</h1>
</div>

<hr>

<p>欢迎使用基因数据处理软件。该软件可动态生成药物基因组风险报告，以及各种常见病和罕见病的多基因风险因素报告。

<p>启动该系统前，必须先用特定密钥激活系统，进行验证。点击 “获取激活码 ”即可获得该密钥。

<hr>

<h2>登录</h2>

<p>用户可通过用户名和密码登录系统。

<hr>

<h2>主页</h2>

<p>主页是应用程序的主要入口。它包含当前在系统中登记的患者列表，其中包括一些元数据。每个患者都有一个唯一的 ID，用于识别特定患者。用户可使用所附的条形码扫描仪扫描病人的 ID 编号，以识别其记录。搜索框还支持模糊搜索，以便从系统登记的患者列表中选择特定患者。系统用户选择患者后可点击 “查看该记录”，获取患者报告。

<hr>

<h2>查看纪录/报告生成</h2>
<p>在 “报告生成 ”页面中，用户可以查看两种类型的基因组报告：用药分析和疾病风险分析。点击左侧列表中的疾病名称后，报告就会显示在右侧窗口中。用户还可以在右侧顶部的搜索框中搜索疾病名称。另外，用户可通过相应按钮保存报告（HTML 网页）或打印报告。原始 VCF 文件也可以保存，但前提是该患者必须有此文件。

<hr>

<h2>患者数据管理器</h2>
<p>患者数据管理器支持患者数据和系统数据的管理。用户可以在此页面看到当前可用的磁盘空间。此页面提供清理缓存的功能，可删除缓存文件，释放磁盘空间。请注意，系统不应在磁盘空间已满的情况下运行。该页面的表格中列出了以下患者元数据项：患者 ID、使用的磁盘空间以及数据是否已打包、VCF 和 CRAM 文件是否可用。系统管理员还可以选择从系统中删除选定的患者。

<hr>

<h2>用户管理（只有管理员可用）</h2>
<p>此页面只有管理员用户可用。它允许管理员用户添加新用户、修改用户密码和注销用户。

<hr>

<h2>系统设置</h2>

<p>该页面允许用户检查软件更新，并显示当前安装的系统版本。用户还可以更改系统语言，目前支持中文和英文。

<hr>

<h2>帮助页面</h2>
<p>该页面展示帮助文档，以及系统版本和数据库版本。

<hr>

<h2>版权</h2>
<p>该软件版权归中基科生物科技有限公司所有。

<hr>
<h6 style='text-align:right'>(c) 2024 中基科生物科技有限公司</h6>

</body>
</html>
'''

########################################################
# Doctorend Help EN
########################################################

doctor_help_text_en = f'''

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
  <h1 style="text-align: right;">Help</h1>
</div>

<hr>

<p>Welcome to the Drug Gene Analysis Front end software. This software allows the dynamic generation of reports for pharmacogenomic risks, and general polygenic risk factors for a wide range of common and rare diseases.
<p>To get started the system must first be validated by activating the system with a specific key. This key can be obtained by clicking ‘Get activation code’. It is important that the user copies this code to another location as it will not be provided again. This code will be required each time the system starts up.

<hr>

<h2>Log in screen</h2>
<p>Users can log into the system by username and password.

<hr>

<h2>Home Page</h2>
<p>The home page is the main entry page to the application. It contains the list of patients currently registered in the system, including some meta data. Each patient has a unique ID that should be used to identify the patient. The attached barcode scanner can be used to scan a patient’s ID number to identify their record. The search boxes also support fuzzy searching to select patients from the list of patients registered in the system. Users of the system can select a patient, and then click ‘View this record’ to access the patient reports.

<hr>

<h2>View This Record/Report Generation</h2>
<p>On the Report Generation screen two types of genomic report can be viewed: Drug analysis, and Disease risk analysis. By clicking on the disease name the report is shown in the window on the right. Users can also search for a disease name in the search box in the top let corner. Reports can be exported (as a HTML web page) or printed using the appropriate buttons. The raw VCF file can also be exported, but only if it is available for this patient.

<hr>

<h2>Patient Data Manager</h2>
<p>Patient Data Manager supports the management of patient data and system data. The current available disk space can be seen, along with a function to clean the cache. This will delete cached files to free up disk space. Note that the system should not be run with a full disk. In the table below, the patient IDs, the disk space used, and if the data is packed, VCF and CRAM files are available. System administrators also have the option to delete selected patients from the system.

<hr>

<h2>User Management (Only available for administrator user)</h2>
<p>This page is only available for administrator users. It allows the admin user to add new users, modify a user’s password, and to delete users.

<hr>

<h2>System Settings</h2>
<p>This page allows the user to check for updates to the software and displays the currently installed system version and the database version. Users can also change the language of the system, currently Chinese and English are supported. Network settings checks that the local network is correctly configured.

<hr>

<h2>Help Page</h2>
<p>This page displays the Help text, and the system version and the database version.

<hr>
<h5 style='text-align:right'>(c) 2024 Helixiome</h5>

</body>
</html>
'''

########################################################
# Backend Help EN
########################################################

backend_help_text_en = f'''

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
  <h1 style="text-align: right;">Help</h1>
</div>

<hr>

<p>Welcome to the Genome Analysis software. This software is for the processing of raw sequence data to formats that summarize genetic and pharmacogenetic information about patients. It is designed to encompass a allows the dynamic generation of reports for pharmacogenomic risks, and general polygenic risk factors for a wide range of common and rare diseases.

<p>To get started the system must first be validated by activating the system with a specific key. This key can be obtained by clicking ‘Get activation code’.

<hr>

<h2>Log in screen</h2>
<p>Users can log into the system by username and password.

<hr>

<h2>Home Page</h2>
<p>The home page is the main entry page to the application. It contains the list of patients currently registered in the system. Each patient has a unique ID that should be used to identify the patient. The attached barcode scanner can be used to scan a patient’s ID number to identify their record. The search boxes also support fuzzy searching to select patients from the list of patients registered in the system. Users of the system can select a patient, and then click ‘View this record’ to access the patient reports. New data can be added into the system using the ‘Add New Patient Data’ button.

<hr>

<h2>Add New Patient</h2>
<p>Patient data can be added to this screen. The Patient ID must be a unique identifier for each patient. In the subsequent sections other meta data about the patient can be entered into the system, including the sequencing identifier, name, the institution that sequenced the data, gender and age. Sequencing data can be uploaded as pairs of FASTQ files. Once Add Patient is clicked, the FASTQ data will be copied to the system, and the patient data will be added to the analysis queue.

<hr>

<h2>Task Analysis Status</h2>
<p>This page shows the current analysis stage of the system. It shows the stage completion for the currently analysis, as well as the number of samples on the queue. The system is automatic, and will process the queue in order.

<hr>

<h2>View This Record/Report Generation</h2>
<p>On the Report Generation screen two types of genomic report can be viewed: Drug analysis, and Disease risk analysis. By clicking on the disease name the report is shown in the window on the right. Users can also search for a disease name in the search box in the top let corner. Reports can be exported (as a HTML web page) or printed using the appropriate buttons. The raw VCF file can also be exported, but only if it is available for this patient.

<hr>

<h2>Patient Data Manager</h2>
<p>Patient Data Manager supports the management of patient data and system data. The current available disk space can be seen, along with a function to clean the cache. This will delete cached files to free up disk space. Note that the system should not be run with a full disk. In the table below, the patient IDs, the disk space used, and if the data is packed, VCF and CRAM files are available. System administrators also have the option to delete selected patients from the system.

<hr>

<h2>User Management (Only available for administrator user)</h2>
<p>This page is only available for administrator users. It allows the admin user to add new users, modify a user’s password, and to delete users.

<hr>

<h2>System Settings</h2>
<p>This page allows the user to check for updates to the software and displays the currently installed system version and the database version. Users can also change the language of the system, currently Chinese and English are supported. Network settings checks that the local network is correctly configured.

<hr>

<h2>Help Page</h2>
<p>This page displays the Help text, and the system version and the database version.

<hr>
<h5 style='text-align:right'>(c) 2024 Helixiome</h5>

</body>
</html>
'''

########################################################
# Backend Help CN
########################################################

backend_help_text_cn = f'''

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
  <h1 style="text-align: right;">帮助文档</h1>
</div>

<hr>

<p>欢迎使用药物基因分析软件。该软件用于处理原始测序数据，并将其转换成能概括患者遗传信息和药物基因组信息的格式。该软件可动态生成药物基因组风险报告，以及多种常见病和罕见病的多基因风险因素报告。

<p>启动该系统前，必须先用特定密钥激活系统，进行验证。点击 “获取激活码 ”即可获得该密钥。点击“立即激活”即可激活并使用该系统。

<hr>

<h2>登录</h2>
<p>用户可通过用户名和密码登录系统。

<hr>

<h2>主页</h2>
主页是应用程序的主要入口。它包含当前在系统中登记的患者列表，其中包括一些元数据。每个患者都有一个唯一的 ID，用于识别特定患者。用户可使用所附的条形码扫描仪扫描病人的 ID 编号，以识别其记录。搜索框还支持模糊搜索，以便从系统登记的患者列表中选择特定患者。系统用户选择患者后可点击 “查看该记录”，获取患者报告。点击 "添加新患者数据 "按钮可将新数据添加到系统中。

<hr>

<h2>添加新患者</h2>
<p>用户可在该页面添加患者数据。需注意每个患者的 ID必须是唯一的。随后可将患者的其他元数据输入系统，包括测序ID、姓名、测序机构、性别和年龄。测序数据为成对的 FASTQ 文件格式。点击“添加患者”后，FASTQ 数据将被复制到系统中，患者数据也将被添加到分析队列中。

<hr>

<h2>任务分析状态</h2>
<p>该页面显示系统当前的分析阶段。它显示当前分析阶段的完成情况以及分析队列中的样本数量。该系统是自动化的，将按顺序处理队列中的样本。

<hr>

<h2>查看纪录/报告生成</h2>
<p>在 “报告生成 ”页面中，用户可以查看两种类型的基因组报告：用药分析和疾病风险分析。点击左侧列表中的疾病名称后，报告就会显示在右侧窗口中。用户还可以在右侧顶部的搜索框中搜索疾病名称。另外，用户可通过相应按钮保存报告（HTML 网页）或打印报告。原始 VCF 文件也可以保存，但前提是该患者必须有此文件。

<hr>

<h2>患者数据管理器</h2>
<p>患者数据管理器支持患者数据和系统数据的管理。用户可以在此页面看到当前可用的磁盘空间。此页面提供清理缓存的功能，可删除缓存文件，释放磁盘空间。请注意，系统不应在磁盘空间已满的情况下运行。该页面的表格中列出了以下患者元数据项：患者 ID、使用的磁盘空间以及数据是否已打包、VCF 和 CRAM 文件是否可用。系统管理员还可以选择从系统中删除选定的患者。

<hr>

<h2>用户管理（只有管理员可用）</h2>
<p>此页面只有管理员用户可用。它允许管理员用户添加新用户、修改用户密码和注销用户。

<hr>

<h2>系统设置</h2>
<p>该页面允许用户检查软件更新，并显示当前安装的系统版本。用户还可以更改系统语言，目前支持中文和英文。

<hr>

<h2>帮助页面</h2>
<p>该页面展示帮助文档，以及系统版本，并能获取详细的软件说明书。

<hr>
<h5 style='text-align:right'>(c) 2024 中基科生物科技有限公司</h5>

</body>
</html>
'''

def get_help(end_type, lang='CN'):
    assert end_type in ('Doctorend', 'Backend'), f'{end_type} not found'
    # load the correct end_type help;

    if end_type == 'Doctorend':
        if lang == 'CN':
            return doctor_help_text_cn
        elif lang == 'EN':
            return doctor_help_text_en

    # TODO: Add Backened text
    if end_type == 'Backend':
        if lang == 'CN':
            return backend_help_text_cn
        elif lang == 'EN':
            return backend_help_text_en

    return None
