

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
        'fail_sec_check_mac':        "Failed security check (Machine)",

        # user manipulation errors
        'user_exists':               "CN A user with this username already exists",
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
        'cleanup_done':              'CNCleanup completed',

        # System registration
        'system_registered':         'System already registered',
        'validation_enc_fail':       'Validation encryption failure',
        'sys_not_registered':        'System not registered',

        # miscellaneous messages:
        'none':                      '无',
        'unk':                       'Unknown Error',
        },
    }
