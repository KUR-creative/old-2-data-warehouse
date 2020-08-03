''' 'image only' means each relation is (img,img). '''
from dw.db import orm
from dw.db import schema as S


def valid():
    return True
def load():
    with orm.session() as sess:
        return sess.query(S.data.uuid).filter(
            S.data.type == 'image' # TODO: remove magic-string
        ).all() # TODO: ?
def process(img_id_rows):
    return (x.uuid for x in img_id_rows)
def canonical(img_idseq):
    return S.identity_data_rel_rowseq(img_idseq, 'only_img')
