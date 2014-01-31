from path import path

from clld.tests.util import TestWithApp

import ids


class Tests(TestWithApp):
    __cfg__ = path(ids.__file__).dirname().joinpath('..', 'development.ini').abspath()
    __setup_db__ = False

    def test_home(self):
        self.app.get('/', status=200)

    def test_contribution(self):
        self.app.get('/contributions', status=200)
        self.app.get('/contributions.geojson', status=200)
        self.app.get('/contributions?iEcho=1', status=200, xhr=True)
        self.app.get('/languages?iEcho=1', status=200, xhr=True)
        self.app.get('/contributions/215', status=200)

    def test_parameter(self):
        self.app.get('/parameters', status=200)
        self.app.get('/parameters?iEcho=1', status=200, xhr=True)
        self.app.get('/parameters/1-222', status=200)
        self.app.get('/parameters/1-222.geojson', status=200)
        self.app.get('/values?parameter=1-222&iEcho=1', status=200, xhr=True)
