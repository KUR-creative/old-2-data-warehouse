from dw.db import orm
from dw.db import schema as S

def canonical_forms(cfseq):
    with orm.session() as sess:
        for cf in cfseq:
            if cf == S.COMMIT:
                sess.commit()
            else:
                sess.add(cf)
        sess.commit()
