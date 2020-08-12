import subprocess

from dw.db import schema as S
from dw.db import orm


def git_hash():
    return (subprocess
       .check_output(['git', 'rev-parse', 'HEAD'])
       .strip().decode('utf8'))

def cli_cmd(cmd, note=None):
    with orm.session() as sess:
        sess.add(S.executed_command(
            command=cmd, git_hash=git_hash(), note=note))
