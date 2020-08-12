''' 
CLI interface of data warehouse.

All successful commands are logged in connected DB.
If you want to know function of a command?

Run command with --help

----
If you want to dump help page to stdout, use linux cmd: column.
ex) $ python main.py generate easy_only --help | column

----
to dev: Don't forget to edit docstring when functions changed!
'''


def init(conn, note=None):
    '''
    Initialize DB. Schema is defined in dw.db.schema
    
    This commands should be executed only once. 
    But if init twice, nothing happens.
    
    args: 
    conn: db connection string. 'id:pw@host:port/dbname' format
    note: note for running command. If not None, it is logged.
    '''
    from dw.db import orm
    from dw.db import query as Q
    from dw.ui import log

    orm.init(conn)
    Q.CREATE_TABLES()
    log.cli_cmd(conn, note)

# TODO: split to module. subcmd or something..
class data(object):
    ''' Add data to DB (not dataset) '''
    def manga109(self, conn, root, note=None):
        '''
        Add manga109 data into db.
        
        Manga109 consists directory of files.
        root directory must be satisfy following structure.
        root
        ├── images
        │   ├── AisazuNihaIrarenai
        │   │   ├── AisazuNihaIrarenai_0.jpg
        │   │   ├── ...
        │   │   └── AisazuNihaIrarenai_100.jpg
        │   ├── AkkeraKanjinchou
        │   ├── ...
        │   └── YumeNoKayoiji
        └── manga109-annotations
            ├── AisazuNihaIrarenai.xml
            ├── Akuhamu.xml
            ├── ...
            └── YumeNoKayoiji.xml
        
        name of directories in images and manga109-annotations 
        must be same in each directories.
        [result]
        It save all images and annotation xmls to DB.
        
        args: 
        conn: connection str. 'id:pw@host:port/dbname' format.
        root: root directory path string of manga109 data.
        note: note for running command. If not None, it is logged.
        '''
        from dw.api import make, put
        from dw.db import orm
        from dw.entity.data import manga109
        from dw.ui import log

        orm.init(conn)
        put.canonical_forms( make.data(manga109)(root) )
        log.cli_cmd(conn, note)
