from __future__ import unicode_literals

from clld.db.meta import DBSession
from clld.db.models.common import Language
from clld.web.adapters.geojson import GeoJsonParameter, GeoJsonLanguages
from clld.interfaces import IParameter, IContribution, IIndex


class GeoJsonMeaning(GeoJsonParameter):
    def feature_properties(self, ctx, req, valueset):
        return {'label': ', '.join(v.name for v in valueset.values)}


class GeoJsonDictionaries(GeoJsonLanguages):
    """Render a collection of languages as geojson feature collection.
    """
    def feature_iterator(self, ctx, req):
        return DBSession.query(Language)


def includeme(config):
    config.register_adapter(GeoJsonMeaning, IParameter)
    config.register_adapter(GeoJsonDictionaries, IContribution, IIndex)
