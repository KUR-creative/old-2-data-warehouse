

from dw.db import schema as S
from dw.util import fp

from pprint import pprint
#print(N)
#pprint(fp.pub_attr_names(N))
for attr in fp.pub_attrs(S):
    if hasattr(attr, '__tablename__'):
        print(attr.__name__)

        
print("g:", globals(), 'l', locals(), 'v', vars())
#pprint(locals())
pprint(vars())

S.generate_names_file()
#pprint(S.asdf)
#pprint(S.names)
'''
import os
conn = os.environ['conn']
m109 = os.environ['m109']
orm.init(T.connection(conn))
Q.DROP_ALL()
Q.CREATE_TABLES()
from dw.api import make, put
from dw.entity.data import manga109

cfs = make.data(manga109)(m109)
put.data(cfs)


with orm.session() as sess:
    id = uuid4()
    data = S.data(T.Data(id))
    datums = [S.data(T.Data()), S.data(T.Data()),
              S.data(T.Data()), S.data(T.Data())]
    sess.add_all(datums)
    sess.add(data)
    sess.commit()
    # ForeignKey가 되려면 먼저 commit을 해야하는 거 같음.
    # 그러니까 data만 특수취급 해야 될 거 같은데? 더 해보고..
    # data-rel도 문제 생길 수 있겠다.
    # data -> annotation -> data-relation 이 순서로 해야 됨..
    # 그러면 cf의 순서가 중요할 수 있겠는데..?
    sess.add(S.file(uuid=data.uuid, path='ppap/bbab'))
    sess.add(S.file(uuid=datums[0].uuid, path='ppap/bbab123'))
    sess.commit()
    result2 = sess.query(S.file)
    result = sess.query(S.data) # select는 나중에..?
from pprint import pprint
print('===============>')
pprint(list(result))
pprint(list(result2))
    
Q.DROP_ALL()
'''
