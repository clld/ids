# Releasing https://ids.clld.org

- Install the software:
  ```shell
  git clone https://github.com/clld/ids
  git clone https://github.com/intercontinental-dictionary-series/ids-internal
  cd ids
  pip install -e .[test]
  ```
- Initialize the DB running
  ```shell
  clld initdb --glottolog ../../glottolog/glottolog --concepticon ../../concepticon/concepticon-cldf/raw/concepticon-data development.ini
  ```
- Run test suite:
  ```shell
  pytest
  ```
- Store the tested requirements:
  ```shell
  pip freeze > requirements.txt
  ```
- Store a db dump:
  ```shell
  pg_dump -xO ids > ids.sql
  zip ids.sql.zip ids.sql
  rm ids.sql
  ```