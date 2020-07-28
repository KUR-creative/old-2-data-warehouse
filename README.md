# data-warehouse

data management system for SickZil-Machine

# commands
### subs
\<F9\> `mypy --show-error-code` \
`pytest --conn id:pw@localhost:port/dbname --m109 m109=/path/to/manga109/dset/root`

### full
`sh env.sh` \
`cd data-warehouse` \
`sh check.sh`

or \
`export conn=id:pw@localhost:port/dbname` \
`export m109=/path/to/manga109/dset/root` \
`sh check.sh`
