from pyramid.config import Configurator

from clld.web.adapters.base import adapter_factory
from clld.web.adapters.cldf import CldfConfig
from clld.db.models.common import Value, Parameter
from clld.interfaces import ILinkAttrs, IMapMarker, IContribution, IValue, ILanguage, ICldfConfig
from clld_glottologfamily_plugin.util import LanguageByFamilyMapMarker

# we must make sure custom models are known at database initialization!
from ids import models
from ids.interfaces import IChapter, IProvider


_ = lambda a: a
_('Contribution')
_('Contributions')
_('Parameter')
_('Parameters')
_('Provider')
_('Providers')
_('Value')
_('Values')


class IDSCldfConfig(CldfConfig):
    def custom_schema(self, req, ds):
        ds.add_columns('FormTable', 'transcription', 'alt_form', 'alt_transcription')
        ds.add_columns('ParameterTable', 'Concepticon_ID')

    def convert(self, model, item, req):
        res = CldfConfig.convert(self, model, item, req)
        if model == Value:
            res['transcription'] = item.word.description
            res['alt_form'] = item.word.alt_name
            res['alt_transcription'] = item.word.alt_description
            res['Source'] = [r.source.id for r in item.valueset.contribution.references]
        if model == Parameter:
            res['Concepticon_ID'] = item.concepticon_id
        return res


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
    config.registry.registerUtility(IDSCldfConfig(), ICldfConfig)
    config.register_adapter(adapter_factory(
        'contribution/detail_tab.mako',
        mimetype='application/vnd.clld.tab',
        send_mimetype="text/plain",
        extension='tab',
        name='tab-separated values'), IContribution)
    config.register_resource('chapter', models.Chapter, IChapter, with_index=True)
    config.register_resource('provider', models.Provider, IProvider, with_index=True)
    return config.make_wsgi_app()
