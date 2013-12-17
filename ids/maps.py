from clld.web.maps import ParameterMap, LanguageMap


class MeaningMap(ParameterMap):
    def get_options(self):
        return {'show_labels': True}


class ContributionMap(LanguageMap):
    """small map on contribution detail page
    """
    def __init__(self, ctx, req, eid='map'):
        super(ContributionMap, self).__init__(ctx.language, req, eid=eid)


def includeme(config):
    config.register_map('parameter', MeaningMap)
    config.register_map('contribution', ContributionMap)
