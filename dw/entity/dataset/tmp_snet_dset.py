from typing import Tuple, Callable, Iterable, List
import funcy as F

from dw.db import orm
from dw.db import schema as S


def valid(mask_group,
          size: int,
          rdt: Tuple[int,int,int],
          split_rdt: Callable[[Iterable], List]):
    # Get dset version from arguments?
    # Check duplication of dset version?
    assert size == sum(rdt)
    return True

def load(mask_group,
         size: int,
         rdt: Tuple[int,int,int],
         split_rdt: Callable[[List], List]):
    ''' split_rdt(seq): seq => id_pairs[train|dev|test] '''
    with orm.session() as sess:
        return (
            size,
            rdt,
            split_rdt([
                (r.aid, r.bid) for r in
                sess.query(
                    S.data_relation.aid,
                    S.data_relation.bid,
                    S.annotation.group,
                )
                .join(S.annotation,
                      S.data_relation.bid == S.annotation.uuid)
                .filter(S.annotation.type == 'text.mask')
                .filter(S.annotation.group == mask_group)
                .all()
            ]),
        )

def select(loaded):
    size, (n_train, n_dev, n_test), ab_pairs = loaded
    total = n_train + n_dev + n_test

    train_abs = ab_pairs[:n_train]
    dev_abs = ab_pairs[n_train: n_train + n_dev]
    test_abs = ab_pairs[n_train + n_dev: total]
    assert total == len(train_abs + dev_abs + test_abs)
    
    return train_abs, dev_abs, test_abs

def canonical(aid_bid_pairs_tuple):
    train_abs, dev_abs, test_abs = aid_bid_pairs_tuple

    train = dict(name='snet.train', revision=0, size=len(train_abs))
    dev = dict(name='snet.dev', revision=0, size=len(dev_abs))
    test = dict(name='snet.test', revision=0, size=len(test_abs))
    
    rowseq = S.help.named2rel_rowseq
    def keys(prefix):
        return F.partial(F.walk_keys, lambda k: f'{prefix}_{k}')
    return F.concat(
        # Make named_relations(relations' name)
        [S.named_relations(**train),
         S.named_relations(**dev),
         S.named_relations(**test),
         S.COMMIT],
        # Make data_rel:rel_name relation
        rowseq(train['name'], train['revision'], train_abs),
        rowseq(dev['name'], dev['revision'], dev_abs),
        rowseq(test['name'], test['revision'], test_abs),
        # Make dataset
        [S.dataset(**keys('train')(train),
                   **keys('dev')(dev),
                   **keys('test')(test))]
    )
