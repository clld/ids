from clld.web.maps import ParameterMap, LanguageMap, Map


class MeaningMap(ParameterMap):
    def get_options(self):
        return {'show_labels': True, 'max_zoom': 10, 'icon_size': 20}


class ContributionMap(LanguageMap):
    """small map on contribution detail page
    """
    def __init__(self, ctx, req, eid='map'):
        super(ContributionMap, self).__init__(ctx.language, req, eid=eid)

    def get_options(self):
        return {'max_zoom': 10, 'icon_size': 20}


class ContributionsMap(Map):
    def get_options(self):
        return {'max_zoom': 10, 'icon_size': 20}


def includeme(config):
    config.register_map('parameter', MeaningMap)
    config.register_map('contribution', ContributionMap)
    config.register_map('languages', ContributionsMap)
