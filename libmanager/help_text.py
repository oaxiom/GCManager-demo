#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):

help_text_cn = '''

<!DOCTYPE html>
<html>
<head>
</head>
<body>

Help text here;

</body>
</html>
'''

help_text_en = '''

<!DOCTYPE html>
<html>
<head>
</head>
<body>

Help text here;

</body>
</html>
'''

def get_help(end_type, lang='CN'):
    # load the correct end_type help;

    if lang == 'CN':
        return help_text_cn#.format(end_type_help)
    elif lang == 'EN':
        return help_text_en#.format(end_type_help)

    return None

