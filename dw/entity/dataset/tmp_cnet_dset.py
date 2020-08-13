import funcy as F

from dw.db import orm
from dw.db import schema as S


def valid():
    # Get dset version from arguments?
    # Check duplication of dset version?
    return True

def load():
    with orm.session() as sess:
        return [
            x.uuid for x in sess.query(S.data.uuid).filter(
                S.data.type == 'image').all() # TODO: remove magic-string
        ]

def select(ids):
    n_train = 70; n_dev = 20; n_test = 10
    total = n_train + n_dev + n_test

    train_ids = ids[:n_train]
    dev_ids = ids[n_train: n_train + n_dev]
    test_ids = ids[n_train + n_dev: total]
    assert total == len(train_ids + dev_ids + test_ids)
    
    return train_ids, dev_ids, test_ids

def canonical(ids_tuple):
    train_ids, dev_ids, test_ids = ids_tuple

    train = dict(name='m109.train', revision=0, size=len(train_ids))
    dev = dict(name='m109.dev', revision=0, size=len(dev_ids))
    test = dict(name='m109.test', revision=0, size=len(test_ids))
    
    rowseq = S.help.identity_named2rel_rowseq
    def keys(prefix):
        return F.partial(F.walk_keys, lambda k: f'{prefix}_{k}')
    return F.concat(
        # Make named_relations(relations' name)
        [S.named_relations(**train),
         S.named_relations(**dev),
         S.named_relations(**test),
         S.COMMIT],
        # Make data_rel:rel_name relation
        rowseq(train['name'], train['revision'], train_ids),
        rowseq(dev['name'], dev['revision'], dev_ids),
        rowseq(test['name'], test['revision'], test_ids),
        # Make dataset
        [S.dataset(**keys('train')(train),
                   **keys('dev')(dev),
                   **keys('test')(test))]
    )
