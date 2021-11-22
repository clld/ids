ids
===

Intercontinental Dictionary Series

Dependencies
------------

requires [pg_collkey](https://www.public-software-group.org/pg_collkey).

```sh
sudo apt install libicu-dev icu-devtools postgresql-server-dev-all
curl -O https://www.public-software-group.org/pub/projects/pg_collkey/v0.5/pg_collkey-v0.5.tar.gz
tar -xzf pg_collkey-v0.5.tar.gz
cd pg_collkey-c5.0
```

Before compiling adjust in `Makefile` the path variables ICU_CFLAGS,
ICU_LDFLAGS, PG_INCLUDE_DIR, PG_PKG_LIB_DIR according to your OS and
settings.  E.g. on Ubuntu change ICU_CFLAGS and ICU_LDFLAGS to the
following:

```make
ICU_CFLAGS = `pkg-config --clfags icu-uc`
ICU_LDFLAGS = `pkg-config --libs icu-uc`
```

Now compile and install:

```sh
make && sudo make install
```
