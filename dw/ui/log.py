import re
import subprocess
import sys

from dw.db import schema as S
from dw.db import orm


connect_re = re.compile('.+:.+@.+:[0-9]+\/.+') # very generous
def cli_cmd(conn, note=None):
    ''' 
    Note - It uses command from sys.argv.
    So it doesn't need explicit command information in args.
    
    args:
    conn: db spec, string 'id:pw@host:port/dbname' format
    note: note for running command. If not None, it is logged.
    '''
    safe_argv = [
        '<connection>' if connect_re.match(arg) else arg
        for arg in sys.argv
    ]
    
    cmd = ' '.join([
        'python',
        *map(lambda arg: repr(arg) if ' ' in arg else arg,
             safe_argv)]
    )
    
    save_command(cmd, note)
    
#---------------------------------------------------------------
def save_command(cmd, note=None):
    with orm.session() as sess:
        sess.add(S.executed_command(
            command=cmd, git_hash=git_hash(), note=note))
        
def git_hash():
    return (subprocess
       .check_output(['git', 'rev-parse', 'HEAD'])
       .strip().decode('utf8'))

