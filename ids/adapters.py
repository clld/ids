from __future__ import unicode_literals

from clld.db.meta import DBSession
from clld.db.models.common import Language, Identifier
from clld.web.adapters.geojson import GeoJsonParameter, GeoJsonLanguages
from clld.web.adapters.cldf import CldfDataset
from clld.interfaces import IParameter, IContribution, IIndex, ICldfDataset


class GeoJsonMeaning(GeoJsonParameter):
    def feature_properties(self, ctx, req, valueset):
        return {
            'values': list(valueset.values),
            'label': ', '.join(v.name for v in valueset.values)}


class GeoJsonDictionaries(GeoJsonLanguages):
    """Render a collection of languages as geojson feature collection.
    """
    def feature_iterator(self, ctx, req):
        return DBSession.query(Language)


class CldfDictionary(CldfDataset):
    def columns(self, req):
        return [
            'ID',
            {
                'name': 'Language_ID',
                'valueUrl': Identifier(type='glottolog', name='{Language_ID}').url()},
            'Language_name',
            {
                'name': 'Parameter_ID',
                'valueUrl': 'http://concepticon.clld.org/parameters/{Parameter_ID}'},
            'Value',
            'Transcription',
            'Concept',
            'Source',
            'Comment',
            'AlternativeValue',
            'AlternativeTranscription',
        ]

    def refs_and_sources(self, req, value):
        if not hasattr(self, '_refs_and_sources'):
            self._refs_and_sources = CldfDataset.refs_and_sources(self, req, self.obj)
        return self._refs_and_sources

    def row(self, req, value, refs):
        return [
            value.id,
            self.obj.language.glottocode,
            self.obj.language.name,
            value.valueset.parameter.concepticon_id,
            value.word.name,
            self.obj.default_representation,
            value.valueset.parameter.name,
            refs,
            value.valueset.comment or '',
            value.valueset.alt_representation or '',
            self.obj.alt_representation or '',
        ]


def includeme(config):
    config.register_adapter(GeoJsonMeaning, IParameter)
    config.register_adapter(CldfDictionary, IContribution, ICldfDataset, name='cldf')
    config.register_adapter(GeoJsonDictionaries, IContribution, IIndex)
