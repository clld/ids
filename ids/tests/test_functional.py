from clldutils.path import Path
from clld.tests.util import TestWithApp

import ids


class Tests(TestWithApp):
    __cfg__ = Path(ids.__file__).parent.joinpath('..', 'development.ini').resolve()
    __setup_db__ = False

    def test_home(self):
        self.app.get_html('/')

    def test_contribution(self):
        self.app.get_html('/contributions')
        self.app.get_html('/contributions/500')
        self.app.get_html('/contributions.geojson')
        self.app.get_dt('/contributions')
        self.app.get_dt('/languages')
        self.app.get_html('/contributions/215')
        self.app.get_dt('/values?contribution=220&iSortingCols=1&iSortCol_0=0')
        self.app.get_dt('/values?contribution=220&iSortingCols=1&iSortCol_0=2')
        self.app.get_dt('/values?contribution=220&sSearch_0=1&sSearch_2=4')

    def test_contributor(self):
        self.app.get_html('/contributors')
        self.app.get_dt('/contributors')

    def test_parameter(self):
        self.app.get_html('/parameters')
        r = self.app.get_dt('/parameters')
        assert r 
        self.app.get_dt('/parameters?chapter=1')
        self.app.get_html('/parameters/1-222')
        self.app.get_json('/parameters/1-222.geojson')
        self.app.get_dt('/values?parameter=1-222')

    def test_language(self):
        self.app.get_html('/languages/182.snippet.html')
        self.app.get_html('/languages/128.snippet.html?parameter=962')
