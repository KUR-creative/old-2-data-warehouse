# conn=id:pw@host:port/dbname
# m109=/path/to/manga109/dataset/root
# export conn
# export m109
pytest --conn $conn --m109 $m109
mypy 
