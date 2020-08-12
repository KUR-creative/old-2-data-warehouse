from dw.db import orm
from dw.db import query as Q
from dw.db import schema as S
from dw.ui import log
from dw.util.test_utils import env_val, skipif_none


def test_logging_cli_cmd(conn):
    conn = env_val(conn=conn)
    skipif_none(conn)
    
    orm.init(conn)
    Q.DROP_ALL()
    Q.CREATE_TABLES()

    with orm.session() as sess:
        cmd = 'cmd'; note = 'test note'
        
        # log cmd
        assert sess.query(S.executed_command).count() == 0
        log.cli_cmd(cmd, note)
        assert sess.query(S.executed_command).count() == 1
        
        row = sess.query(S.executed_command).first()
        assert row.command == cmd
        assert row.note == note
        sess.commit()
        
        # log cmd2
        assert sess.query(S.executed_command).count() == 1
        log.cli_cmd(cmd + '2')
        assert sess.query(S.executed_command).count() == 2
        
        rows = list(sess.query(S.executed_command)
                        .order_by(S.executed_command.timestamp)
                        .all())
        assert rows[0].timestamp < rows[1].timestamp
        assert rows[0].git_hash == rows[1].git_hash
