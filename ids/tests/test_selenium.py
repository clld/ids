from clld.tests.util import TestWithSelenium

import ids


class Tests(TestWithSelenium):
    app = ids.main({}, **{'sqlalchemy.url': 'postgres://robert@/ids'})
