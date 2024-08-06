

errormsgs = {
    'EN': {
        # Security
        'fail_sec_check_mac':        "Failed security check (Machine)",

        # user manipulation errors
        'user_exists':               "A user with this username already exists",
        'user_not_exists':           'This user {username} does not exist',
        'user_success_registration': "Successful registration",
        'old_password_reqd':         "Old password is required",
        'incorrect_old_pass':        "Incorrect old password",
        'oldpass_is_newpass':        "Password is the same as old password",
        'changed_pass':              'Succesfully changed password for user {username}',
        'user_not_admin':            "The current user is not an admin",
        'del_user_not_exist':        "A user with this username {username_to_delete} does not exist",
        'cannot_del_admin':          "An admin user cannot be deleted",
        'user_deleted':              "{username_to_delete} succesfully deleted",

        # Patient_id errors
        'pid_not_found':             '{patient_id} not found',
        'pid_exists':                '{patient_id} already exists',
        'pid_not_exist':             '{patient_id} does not exist',

        'analysis_not_complete':     'Analysis is not complete for {patient_id}',
        'end_type_not_set':          'end_type has not been set',

        # Upload file errors
        'doc_only_one_file':         'Doctor end expects only one file',
        'doc_wrong_file_format':     'Doctor end expects a single file in the format .gcm or .vcf.gz',
        'ana_even_files':            'Analysis end expects an even number of files, one for each read pair',
        'ana_wrong_file_format':     'File format appears incorrect, ".fastq.gz" is missing in file {f}',
        'upload_error':              'Upload file error',

        # Others;
        'cleanup_done':              'Cleanup completed',

        # System registration
        'system_registered':         'System already registered',
        'validation_enc_fail':       'Validation encryption failure',
        'sys_not_registered':        'System not registered',

        # miscellaneous messages:
        'none':                      'None',
        'unk':                       'Unknown Error',
        },
    'CN': {
        # Security
        'fail_sec_check_mac':        "系统安全检查失败",

        # user manipulation errors
        'user_exists':               "该用户名已存在",
        'user_not_exists':           '用户名 {username} 不存在',
        'user_success_registration': "注册成功",
        'old_password_reqd':         "请输入旧密码",
        'incorrect_old_pass':        "旧密码输入错误",
        'oldpass_is_newpass':        "新密码与旧密码不能一致",
        'changed_pass':              '成功修改用户 {username} 密码',
        'user_not_admin':            "当前用户不是管理员",
        'del_user_not_exist':        "用户名 {username_to_delete} 不存在",
        'cannot_del_admin':          "不能删除管理员用户",
        'user_deleted':              "已成功删除 {username_to_delete} ",

        # Patient_id errors
        'pid_not_found':             '未找到 {patient_id} ',
        'pid_exists':                '{patient_id} 已存在',
        'pid_not_exist':             '{patient_id} 不存在',

        'analysis_not_complete':     '对 {patient_id} 的分析还未完成',
        'end_type_not_set':          '还未设置端的类型，请设置医生端或分析端',

        # Upload file errors
        'doc_only_one_file':         '医生端只接受一个文件',
        'doc_wrong_file_format':     '医生端只接受单个格式为.gcm 或 .vcf.gz格式的文件',
        'ana_even_files':            '分析端只接受偶数个文件，每组文件分别为左右两端配对读数',
        'ana_wrong_file_format':     '文件格式错误, ".fastq.gz" 后缀在 {f} 中缺失',
        'upload_error':              '上传文件出错',

        # Others;
        'cleanup_done':              '清理成功',

        # System registration
        'system_registered':         '系统已激活',
        'validation_enc_fail':       '加密验证失败',
        'sys_not_registered':        '系统未激活',

        # miscellaneous messages:
        'none':                      '无',
        'unk':                       '未知错误',
        },
    }
