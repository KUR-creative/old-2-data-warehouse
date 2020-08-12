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

def init(connection, note=None):
    '''
    Initialize DB. Schema is defined in dw.db.schema
    
    This commands should be executed only once. 
    But if init twice, nothing happens.
    
    args: 
    connection: string 'id:pw@host:port/dbname' format
    note: note for running command. If not None, it be logged.
    '''
    from dw.db import orm
    from dw.db import query as Q

    orm.init(connection)
    Q.CREATE_TABLES()

    print(note)
