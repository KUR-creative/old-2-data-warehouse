import fire

from dw.ui import cli


if __name__ == '__main__':
    fire.Fire(cli)
'''
from dw.ui import cli

from dw.util.test_utils import env_val, skipif_none


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
'''
