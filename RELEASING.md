# Releasing https://ids.clld.org

Install the software:
```shell
git clone https://github.com/clld/ids
git clone --branch v5.3 --depth 1 https://github.com/glottolog/glottolog
git clone --branch v3.4.0 --depth 1 https://github.com/concepticon/concepticon-data
git clone https://github.com/intercontinental-dictionary-series/ids-internal
cd ids
pip install -e .[test]
```
Initialize the DB running
```shell
clld initdb --glottolog ../glottolog --concepticon ../concepticon-data development.ini
```
Run test suite:
```shell
pytest
```
Store the tested requirements:
```shell
pip freeze > requirements.txt
```
Store a db dump:
```shell
pg_dump -xO --compress gzip:9 ids > ids.sql.gz
```
