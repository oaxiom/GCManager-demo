#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):

from . import html_data

help_text_cn = f'''

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

<p>欢迎使用药物基因分析前端软件。该软件允许动态生成药物基因组风险报告，以及各种常见和罕见疾病的一般多基因风险因素报告。

<p>要开始使用，必须首先通过使用特定密钥激活系统来验证系统。此密钥可通过单击“获取激活码”获得。用户将此代码复制到另一个位置是很重要的，因为它将不再提供。每次系统启动时都需要此代码。

<hr>

<h2>登录屏幕</h2>
<p>用户可以使用用户名和密码登录系统。

<hr>

<h2>主页</h2>
主页是应用程序的主要入口页面。它包含当前在系统中注册的患者列表，包括一些元数据。每个患者都有一个唯一的ID，应用于识别患者。附带的条形码扫描仪可用于扫描患者的身份证号码，以识别其记录。搜索框还支持模糊搜索，以从系统中注册的患者列表中选择患者。系统用户可以选择一名患者，然后单击“查看此记录”以访问患者报告。

<hr>

<h2>查看此记录/报告生成</h2>
在报告生成屏幕上，可以查看两种类型的基因组报告：药物分析和疾病风险分析。单击疾病名称，报告将显示在右侧的窗口中。用户还可以在左上角的搜索框中搜索疾病名称。报告可以导出（作为HTML网页）或使用适当的按钮打印。原始VCF文件也可以导出，但前提是该文件可用于该患者。

<hr>

<h2>患者数据管理器</h2>
Patient Data Manager支持患者数据和系统数据的管理。可以看到当前可用的磁盘空间，以及清理缓存的功能。这将删除缓存的文件以释放磁盘空间。请注意，系统不应在磁盘已满的情况下运行。在下表中，患者ID、使用的磁盘空间，以及如果数据已打包，则VCF和CRAM文件可用。系统管理员还可以选择从系统中删除选定的患者。

<hr>

<h2>用户管理（仅适用于管理员用户）</h2>
此页面仅适用于管理员用户。它允许管理员用户添加新用户、修改用户密码和删除用户。

<hr>

<h2>系统设置</h2>
此页面允许用户检查软件的更新，并显示当前安装的系统版本和数据库版本。用户还可以更改系统的语言，目前支持中文和英文。网络设置检查本地网络是否已正确配置。

<hr>

<h2>帮助页面</h2>
此页面显示帮助文本、系统版本和数据库版本。

<hr>
<h6 style='text-align:right'>(c) 2024 中基科生物科技有限公司</h6>

</body>
</html>
'''

help_text_en = f'''

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
The home page is the main entry page to the application. It contains the list of patients currently registered in the system, including some meta data. Each patient has a unique ID that should be used to identify the patient. The attached barcode scanner can be used to scan a patient’s ID number to identify their record. The search boxes also support fuzzy searching to select patients from the list of patients registered in the system. Users of the system can select a patient, and then click ‘View this record’ to access the patient reports.

<hr>

<h2>View This Record/Report Generation</h2>
On the Report Generation screen two types of genomic report can be viewed: Drug analysis, and Disease risk analysis. By clicking on the disease name the report is shown in the window on the right. Users can also search for a disease name in the search box in the top let corner. Reports can be exported (as a HTML web page) or printed using the appropriate buttons. The raw VCF file can also be exported, but only if it is available for this patient. 

<hr>

<h2>Patient Data Manager</h2>
Patient Data Manager supports the management of patient data and system data. The current available disk space can be seen, along with a function to clean the cache. This will delete cached files to free up disk space. Note that the system should not be run with a full disk. In the table below, the patient IDs, the disk space used, and if the data is packed, VCF and CRAM files are available. System administrators also have the option to delete selected patients from the system.

<hr>

<h2>User Management (Only available for administrator user)</h2>
This page is only available for administrator users. It allows the admin user to add new users, modify a user’s password, and to delete users. 

<hr>

<h2>System Settings</h2>
This page allows the user to check for updates to the software and displays the currently installed system version and the database version. Users can also change the language of the system, currently Chinese and English are supported. Network settings checks that the local network is correctly configured.

<hr>

<h2>Help Page</h2>
This page displays the Help text, and the system version and the database version.

<hr>
<h5 style='text-align:right'>(c) 2024 Helixiome</h5>

</body>
</html>
'''

def get_help(end_type, lang='CN'):
    # load the correct end_type help;

    if end_type == 'Doctorend':
        if lang == 'CN':
            return help_text_cn
        elif lang == 'EN':
            return help_text_en
    
    # TODO: Add Backened text
    if end_type == 'Backened':
        if lang == 'CN':
            return help_text_cn
        elif lang == 'EN':
            return help_text_en

    return None
