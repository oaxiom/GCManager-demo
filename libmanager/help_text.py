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

NA

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
