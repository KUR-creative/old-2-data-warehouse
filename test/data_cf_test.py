



'''
@st.composite
def rand_datum(draw):
    return types.Data(
        uuid4(), draw(st.sampled_from(types.DataType)))
@given(datums=st.lists(rand_datum()))
@settings(max_examples=20, deadline=300)
@pytest.mark.skip("it's ovious it correct. Test when changed.")
def test_insert(datums, conn):
    conn = env_val(conn=conn)
    skipif_none(datums, conn)
    # insert generated canonical forms of data
    orm.init(conn)
    Q.CREATE_TABLES()
    with orm.session() as sess:
        sess.add_all(F.lmap(S.data, datums))
        # Be Careful!! sess must be in ctx manager!!!
        for inp, out in zip(datums, sess.query(S.data).all()):
            assert inp.uuid == out.uuid
    Q.DROP_ALL()
'''
