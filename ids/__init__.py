from pyramid.config import Configurator

from clld.web.adapters.base import adapter_factory
from clld.interfaces import ILinkAttrs, IMapMarker, IContribution, IValue, ILanguage
from clld_glottologfamily_plugin.util import LanguageByFamilyMapMarker

# we must make sure custom models are known at database initialization!
from ids import models
from ids.interfaces import IChapter


_ = lambda a: a
_('Contribution')
_('Contributions')
_('Parameter')
_('Parameters')
_('Value')
_('Values')


def link_attrs(req, obj, **kw):
    if ILanguage.providedBy(obj):
        # we are about to link to a language details page: redirect to contribution page!
        kw['href'] = req.route_url('contribution', id=obj.id, **kw.pop('url_kw', {}))
    if IValue.providedBy(obj):
        # we are about to link to a value details page: redirect to valueset page!
        kw['href'] = req.resource_url(obj.valueset, **kw.pop('url_kw', {}))
    return kw


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('clldmpg')
    config.registry.registerUtility(LanguageByFamilyMapMarker(), IMapMarker)
    config.registry.registerUtility(link_attrs, ILinkAttrs)
    config.register_adapter(adapter_factory(
        'contribution/detail_tab.mako',
        mimetype='application/vnd.clld.tab',
        send_mimetype="text/plain",
        extension='tab',
        name='tab-separated values'), IContribution)
    config.register_resource('chapter', models.Chapter, IChapter, with_index=True)
    return config.make_wsgi_app()
