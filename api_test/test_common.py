

def cmd_process(cmd):
    print(f'\n>>> {cmd}')
    res = eval(cmd)

    if isinstance(res, str):
        lines = res.split('\n')
        if len(lines) > 10:
            print('\n'.join(lines[0:9]))
            print(f'{len(lines):,} in total')
            return
    elif isinstance(res, list):
        if len(res) > 10:
            print(res[0:9])
            return
    print(res)