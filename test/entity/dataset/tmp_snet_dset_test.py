from dw.util.test_utils import env_val, skipif_none
from dw.ui import cli


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
    assert cli.data.old_snet(conn, snet) == cli.RUN_SUCCESS
    assert cli.data.szmc_v0(conn, v0_m101) == cli.RUN_SUCCESS
    assert cli.data.szmc_v0(conn, v0_school) == cli.RUN_SUCCESS
    
