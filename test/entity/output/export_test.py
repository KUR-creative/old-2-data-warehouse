from dw.api import make, put
from dw.db import schema as S
from dw.entity.dataset import tmp_snet_dset
from dw.entity.output import tfrecord
from dw.ui import cli
from dw.util.test_utils import env_val, skipif_none
from dw.util import fp

#Test snet export
def test_export_tmp_snet_dset(
        conn, snet, v0_m101, v0_school, tmp_path):
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
    
    # Add tmp snet dataset(s)
    put.db_rows(make.dataset(tmp_snet_dset)(
        'all', 20, (10, 6, 4), fp.inplace_shuffled))
    put.db_rows(make.dataset(tmp_snet_dset)(
        'all', 10, (5, 3, 2), fp.inplace_shuffled))
    size = 30; rdt = (15, 10, 5) # tRain, Dev, Test
    put.db_rows(make.dataset(tmp_snet_dset)(
        'all', size, rdt, fp.inplace_shuffled))

    # Select a dataset
    from dw.db import orm
    with orm.session() as sess:
        selected = S.help.row2dict(
            sess.query(S.dataset).filter(
                S.dataset.train_name == 'snet.train',
                S.dataset.dev_name == 'snet.dev',
                S.dataset.test_name == 'snet.test'
            ).order_by(
                S.dataset.train_size.desc()
            ).first())
        
    # select(...) => S.dataset
    rows, files = make.output(tfrecord)(selected, tmp_path) # directory
    put.db_rows(rows); put.files(files) # TODO? put.output ?

    # assert: DB logs exported output artifact
    with orm.session() as sess:
        assert 1 == sess.query(S.exported).count()
        exported = S.help.row2dict(
            sess.query(S.exported).first())
    assert exported.items() >= selected.items()
    
    # assert:
    train_fmt = '{train_revision}_{train_size}'
    dev_fmt = '{dev_revision}_{dev_size}'
    test_fmt = '{test_revision}_{test_size}'
    fmt = f'{train_fmt}.{dev_fmt}.{test_fmt}'
    path = tmp_path / ('snet.' + fmt.format_map(exported))
    
    assert path.exists()
    # Exported tfrecord has same number of images, masks in DB
    # Metadata also same
    # images, masks actually saved - assert same from db

    
#Test cnet export
