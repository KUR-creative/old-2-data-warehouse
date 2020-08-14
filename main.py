'''
import fire

from dw.ui import cli


if __name__ == '__main__':
    fire.Fire(cli)
'''
from dw.ui import cli

from dw.util.test_utils import env_val


conn = snet = v0_m101 = v0_school = None
conn = env_val(conn=conn)
snet = env_val(snet=snet)
v0_m101 = env_val(v0_m101=v0_m101)
v0_school = env_val(v0_school=v0_school)

from dw.db import orm, query as Q
orm.init(conn)
Q.DROP_ALL()
assert cli.init(conn) == cli.RUN_SUCCESS
# Add all data
assert cli.data.old_snet(conn, snet) == cli.RUN_SUCCESS
assert cli.data.szmc_v0(conn, v0_m101) == cli.RUN_SUCCESS
assert cli.data.szmc_v0(conn, v0_school) == cli.RUN_SUCCESS


from dw.entity.dataset import tmp_snet_dset
from dw.api import make, put
from dw.util import fp
size = 30
rdt = (15, 10, 5) # tRain, Dev, Test
put.db_rows(make.dataset(tmp_snet_dset)(
    'all', size, rdt, fp.inplace_shuffled
))

size = 20
rdt = (10, 6, 4) # tRain, Dev, Test
put.db_rows(make.dataset(tmp_snet_dset)(
    'all', size, rdt, fp.inplace_shuffled
))

size = 10
rdt = (5, 3, 2) # tRain, Dev, Test
put.db_rows(make.dataset(tmp_snet_dset)(
    'all', size, rdt, fp.inplace_shuffled
))

from dw.db import schema as S
name = 'snet'
with orm.session() as sess:
    row = sess.query(S.dataset).filter(
        S.dataset.train_name == name + '.train',
        S.dataset.dev_name == name + '.dev',
        S.dataset.test_name == name + '.test'
    ).order_by(
        S.dataset.train_size.desc()
    ).first()
    
    from pprint import pprint
    pprint( {col: getattr(row, col)
            for col in row.__table__.columns.keys()} )

    #pprint(ret)
    #pprint(ret.items())
    #pprint(dict(ret))
    #pprint(ret._asdict())
