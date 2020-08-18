import fire

from dw.ui import cli


if __name__ == '__main__':
    fire.Fire(cli)
'''


from dw.api import make
from dw.entity.data import crop_images

make.data(crop_images)(
    None, [(5, 7), (11, 5)], 2, 3)
exit()

from dw.ui import cli

from dw.util.test_utils import env_val


conn = snet = v0_m101 = v0_school = cfc = None
conn = env_val(conn=conn)
snet = env_val(snet=snet)
v0_m101 = env_val(v0_m101=v0_m101)
v0_school = env_val(v0_school=v0_school)
cfc = env_val(cfc=cfc)

'''

'''
from dw.db import orm, query as Q
orm.init(conn)
Q.DROP_ALL()
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
'''

'''
from dw.db import orm, query as Q
orm.init(conn)
Q.DROP_ALL()
assert cli.init(conn) == cli.RUN_SUCCESS
cli.data.image_directory(conn, cfc)
print('finished')

'''
