from functools import partial

from clld.web.app import get_configurator, menu_item
from clld import interfaces

# we must make sure custom models are known at database initialization!
from ids import models


_ = lambda a: a
_('Contribution')
_('Contributions')
_('Parameter')
_('Parameters')
_('Value')


def link_attrs(req, obj, **kw):
    if interfaces.ILanguage.providedBy(obj):
        # we are about to link to a language details page: redirect to contribution page!
        kw['href'] = req.route_url('contribution', id=obj.id, **kw.pop('url_kw', {}))
    if interfaces.IValue.providedBy(obj):
        # we are about to link to a value details page: redirect to valueset page!
        kw['href'] = req.resource_url(obj.valueset, **kw.pop('url_kw', {}))
    return kw


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    utilities = [
        (link_attrs, interfaces.ILinkAttrs),
    ]
    config = get_configurator('ids', *utilities, settings=settings)
    config.register_menu(
        ('dataset', partial(menu_item, 'dataset', label='Home')),
        ('contributions', partial(menu_item, 'contributions')),
        ('parameters', partial(menu_item, 'parameters')),
        ('sources', partial(menu_item, 'sources')),
        ('contributors', partial(menu_item, 'contributors')),
    )
    config.include('clldmpg')
    config.include('ids.datatables')
    config.include('ids.adapters')
    config.include('ids.maps')
    return config.make_wsgi_app()
