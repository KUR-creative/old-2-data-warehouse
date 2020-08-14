from dw.api import make, put
from dw.db import orm
from dw.db import schema as S
from dw.db import query as Q
from dw.entity.dataset import tmp_snet_dset
from dw.ui import cli
from dw.util.test_utils import env_val, skipif_none
from dw.util import fp


def test_make_and_save_data_rel_chunk_and_dataset(
        conn, snet, v0_m101, v0_school):
    conn = env_val(conn=conn)
    snet = env_val(snet=snet)
    v0_m101 = env_val(v0_m101=v0_m101)
    v0_school = env_val(v0_school=v0_school)
    skipif_none(conn, snet, v0_m101, v0_school)
    
    # Initialize
    assert cli.init(conn) == cli.RUN_SUCCESS
    # Add all data
    #assert cli.data.old_snet(conn, snet) == cli.RUN_SUCCESS
    # We need 'all mask' from old snet.
    assert cli.data.szmc_v0(conn, v0_m101) == cli.RUN_SUCCESS
    assert cli.data.szmc_v0(conn, v0_school) == cli.RUN_SUCCESS

    # Set size
    with orm.session() as sess:
        num_alls = (
            sess.query(S.annotation)
                .filter(S.annotation.type == 'text.mask')
                .filter(S.annotation.group == 'all')
                .count())
    size = 30; assert size < num_alls
    rdt = (15, 10, 5) # tRain, Dev, Test
    # Make and Put snet dataset
    put.db_rows(make.dataset(tmp_snet_dset)(
        'all', size, rdt, fp.inplace_shuffled
    ))
    # Check tables
    with orm.session() as sess:
        assert sess.query(S.named_relations).count() == 3
        assert sess.query(S.named_relations2data_relation).count() \
            == size
        assert sess.query(S.dataset).count() == 1
        # Check content
        row = sess.query(S.named_relations).filter(
            S.named_relations.name == 'snet.train').first()
        assert row.revision == 0; assert row.size == rdt[0]
        row = sess.query(S.named_relations).filter(
            S.named_relations.name == 'snet.dev').first()
        assert row.revision == 0; assert row.size == rdt[1]
        row = sess.query(S.named_relations).filter(
            S.named_relations.name == 'snet.test').first()
        assert row.revision == 0; assert row.size == rdt[2]
        
    Q.DROP_ALL()
