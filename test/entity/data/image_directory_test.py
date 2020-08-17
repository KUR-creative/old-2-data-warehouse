from dw.api import make, put
from dw.db import orm, query as Q
from dw.db import schema as S
from dw.ui import cli
from dw.util.test_utils import env_val, skipif_none
from dw.util import file_utils as fu
from dw.entity.data import image_directory


def test_image_directory(conn, cfc):
    conn = env_val(conn=conn)
    root = env_val(cfc=cfc)
    skipif_none(conn, root)

    orm.init(conn)
    Q.DROP_ALL()
    assert cli.init(conn) == cli.RUN_SUCCESS

    cfs = make.data(image_directory)(root, 'clean_fmd_comics')
    put.db_rows(cfs)

    num_files = len(fu.descendants(root))
    with orm.session() as sess:
        num_files == sess.query(S.data).count()
