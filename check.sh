# conn=id:pw@host:port/dbname
# m109=/path/to/manga109/dataset/root
# export conn
# export m109

# pip install pyflakes, autoflake
autoflake --remove-all-unused-imports -r --in-place --exclude ./dw/util/fp.py . 
pytest --conn $conn --m109 $m109
mypy 
pyflakes .
