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
        self.app.get('/contributions/500', status=200)
        self.app.get('/contributions.geojson', status=200)
        self.app.get('/contributions?sEcho=1', status=200, xhr=True)
        self.app.get('/languages?sEcho=1', status=200, xhr=True)
        self.app.get('/contributions/215', status=200)
        self.app.get('/values?contribution=220&sEcho=1&iSortingCols=1&iSortCol_0=0&sSortDir_0=asc', status=200, xhr=True)
        self.app.get('/values?contribution=220&sEcho=1&iSortingCols=1&iSortCol_0=2&sSortDir_0=asc', status=200, xhr=True)
        self.app.get('/values?contribution=220&sEcho=1&sSearch_0=1&sSearch_2=4', status=200, xhr=True)

    def test_contributor(self):
        self.app.get('/contributors', status=200)
        self.app.get('/contributors?sEcho=1', status=200, xhr=True)

    def test_parameter(self):
        self.app.get('/parameters', status=200)
        self.app.get('/parameters?sEcho=1', status=200, xhr=True)
        self.app.get('/parameters?sEcho=1&chapter=1', status=200, xhr=True)
        self.app.get('/parameters/1-222', status=200)
        self.app.get('/parameters/1-222.geojson', status=200)
        self.app.get('/values?parameter=1-222&sEcho=1', status=200, xhr=True)

    def test_language(self):
        self.app.get('/languages/182.snippet.html', status=200)
        self.app.get('/languages/128.snippet.html?parameter=962', status=200)

