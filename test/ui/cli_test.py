from dw.db import orm
from dw.db import schema as S
from dw.db import query as Q
from dw.util.test_utils import env_val, skipif_none
from dw.ui import cli


def test_cli_commands_can_be_called_as_fn(conn, v0_m101):
    conn, v0_m101 = env_val(conn=conn), env_val(v0_m101=v0_m101)
    skipif_none(conn, v0_m101)
    
    orm.init(conn)
    Q.DROP_ALL()

    init_note = 'init note'
    ret = cli.init(conn, init_note)
    assert ret == cli.RUN_SUCCESS
    with orm.session() as sess:
        assert sess.query(S.executed_command).count() == 1
        assert init_note == sess.query(
            S.executed_command).first().note

    v0_note = 'v0 note'
    ret = cli.data.szmc_v0(conn, v0_m101, v0_note)
    assert ret == cli.RUN_SUCCESS
    with orm.session() as sess:
        assert sess.query(S.executed_command).count() == 2
        assert v0_note == list(
            sess.query(S.executed_command)
                .order_by(S.executed_command.timestamp)
                .all()
        )[1].note
