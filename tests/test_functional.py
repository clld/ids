import pytest


@pytest.mark.parametrize(
    "method,path",
    [
        ('get_html', '/'),
        ('get_html', '/contributions'),
        ('get_html', '/contributions/500'),
        ('get_html', '/contributions.geojson'),
        ('get_dt', '/contributions'),
        ('get_dt', '/languages'),
        ('get_html', '/contributions/215'),
        ('get_dt', '/values?contribution=220&iSortingCols=1&iSortCol_0=0'),
        ('get_dt', '/values?contribution=220&iSortingCols=1&iSortCol_0=2'),
        ('get_dt', '/values?contribution=220&sSearch_0=1&sSearch_2=4'),
        ('get_html', '/contributors'),
        ('get_dt', '/contributors'),
        ('get_html', '/parameters'),
        ('get_dt', '/parameters'),
        ('get_dt', '/parameters?chapter=1'),
        ('get_html', '/parameters/1-222'),
        ('get_json', '/parameters/1-222.geojson'),
        ('get_dt', '/values?parameter=1-222'),
        ('get_html', '/languages/182.snippet.html'),
        ('get_html', '/languages/128.snippet.html?parameter=962'),
    ])
def test_pages(app, method, path):
    getattr(app, method)(path)
