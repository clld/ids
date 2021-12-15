from sqlalchemy import Integer, and_
from sqlalchemy.sql.expression import cast, func
from sqlalchemy.orm import aliased, joinedload, contains_eager

from clld.web.datatables import Values, Sources
from clld.web.datatables.base import Col, LinkCol, LinkToMapCol, DataTable, IntegerIdCol, DetailsRowLinkCol, ExternalLinkCol
from clld.web.datatables.contribution import Contributions, CitationCol
from clld.web.datatables.source import TypeCol
from clld.web.datatables import contributor
from clld.web.datatables.parameter import Parameters
from clld.web.util.glottolog import link as gc_link
from clld.web.util.helpers import link, external_link
from clld.web.util.htmllib import HTML
from clld.db.meta import DBSession
from clld.db.util import icontains
from clld.db.models.common import (
    ValueSet, Value, Identifier, LanguageIdentifier, IdentifierType, Language,
    Parameter, Contribution, ContributionContributor, Contributor)
from clld_glottologfamily_plugin.datatables import MacroareaCol, FamilyCol
from clld_glottologfamily_plugin.models import Family

from ids.models import Chapter, Entry, ROLES, Dictionary, IdsLanguage, Provider


class IDSCodeCol(Col):
    """special handling for IDS code
    """
    __kw__ = {'sTitle': 'IDS code'}

    def format(self, item):
        return self.get_obj(item).id.replace('-', '.')

    def order(self):
        return Entry.chapter_pk, cast(Entry.sub_code, Integer)

    def search(self, qs):
        return Entry.id.contains(qs.replace('.', '-'))


class ChapterCol(Col):
    def __init__(self, *args, **kw):
        kw['choices'] = [
            (sf.pk, sf.name) for sf in DBSession.query(Chapter).order_by(Chapter.pk)]
        super(ChapterCol, self).__init__(*args, **kw)

    def format(self, item):
        obj = self.get_obj(item)
        return obj.chapter.name

    def order(self):
        return Entry.chapter_pk

    def search(self, qs):
        return Entry.chapter_pk == int(qs)


class FormCol(LinkCol):
    def order(self):
        return func.replace(func.replace(Value.name, '`', ''), 'ː', '')


class Counterparts(Values):
    """Lists of counterparts
    """
    def get_options(self):
        opts = super(Values, self).get_options()
        if self.parameter:
            opts["aaSorting"] = [[2, "asc"], [1, "asc"]]
        elif self.contribution:
            opts["aaSorting"] = [[0, "asc"]]
        else:
            opts["aaSorting"] = [[0, "asc"], [4, "asc"], [3, "asc"]]
        return opts

    def base_query(self, query):
        query = Values.base_query(self, query)
        if not self.language and not self.contribution and not self.parameter:
            return DBSession.query(Value).join(ValueSet)\
                .join(ValueSet.language)\
                .join(ValueSet.parameter)\
                .join(IdsLanguage.family, isouter=True)\
                .options(joinedload(Value.valueset).joinedload(ValueSet.language),
                         joinedload(Value.valueset, ValueSet.parameter))
        if self.contribution:
            return query
        if self.parameter:
            return query.join(IdsLanguage.family, isouter=True)
        return query

    def col_defs(self):
        lang = lambda i: i.valueset.language
        param = lambda i: i.valueset.parameter
        if self.parameter:
            res = [
                LinkToMapCol(self, 'm', get_object=lang),
                LinkCol(
                    self, 'language',
                    model_col=Language.name,
                    get_object=lang),
                IdsFamilyCol(
                    self, 'family',
                    language_cls=IdsLanguage,
                    get_object=lambda i: i.valueset.language),
            ]
        elif self.language or self.contribution:
            res = [
                IDSCodeCol(
                    self, 'ids_code',
                    model_col=Parameter.id,
                    get_object=param),
                LinkCol(
                    self, 'meaning',
                    model_col=Parameter.name,
                    get_object=param),
                ChapterCol(self, 'chapter', get_object=param)]
        else:
            res = [
                IDSCodeCol(
                    self, 'ids_code',
                    model_col=Parameter.id,
                    get_object=param),
                LinkCol(
                    self, 'meaning',
                    model_col=Parameter.name,
                    get_object=param),
                ChapterCol(self, 'chapter', get_object=param),
                LinkCol(
                    self, 'language',
                    model_col=Language.name,
                    get_object=lang),
                IdsFamilyCol(
                    self, 'family',
                    language_cls=IdsLanguage,
                    get_object=lambda i: i.valueset.language),
            ]
        res.extend([
            FormCol(
                self, 'counterparts',
                model_col=Value.name,
                sClass="charissil"),
            Col(self, 'description'),
        ])
        return res


class RoleCol(Col):
    __kw__ = {'choices': sorted([r[0] for r in ROLES.values()]), 'sClass': 'left'}

    def format(self, item):
        return ROLES[item.ord][0]

    def search(self, qs):
        ROLE_MAP = {v[0]: k for k, v in ROLES.items()}
        return self.model_col == ROLE_MAP[qs]


class Compilers(contributor.Contributors):
    def base_query(self, query):
        return DBSession.query(ContributionContributor).join(Contribution).join(Contributor).join(Language)

    def col_defs(self):
        return [
            LinkCol(self, 'name', get_object=lambda i: i.contributor, model_col=Contributor.name),
            RoleCol(self, 'role', model_col=ContributionContributor.ord),
            LinkCol(self, 'dictionary', get_object=lambda i: i.contribution, model_col=Contribution.name),
        ]


class ContributorCol(Col):
    __kw__ = {'bSortable': False, 'bSearchable': False}

    def __init__(self, dt, name, roleid, **kw):
        kw['sTitle'] = ROLES[roleid][0]
        Col.__init__(self, dt, name, **kw)
        self.roleid = roleid

    def format(self, item):
        return HTML.ul(
            *[HTML.li(link(self.dt.req, ca.contributor))
              for ca in item.contributor_assocs if ca.ord == self.roleid])


class IdsFamilyCol(FamilyCol):
    def format(self, item):
        item_ = self.get_obj(item)
        if not item_.glottocode:
            return ''
        return FamilyCol.format(self, item)


class IdsGlottocodeCol(Col):
    __kw__ = {"bSortable": False}

    def format(self, item):
        if item.language.glottocode:
            return gc_link(
                self.dt.req,
                item.language.glottocode,
                label=item.language.glottocode)
        else:
            return ""

    def search(self, qs):
        return and_(Identifier.type.__eq__(IdentifierType.glottolog.value),
                    icontains(Identifier.name, qs))


class IdsISOCol(Col):
    __kw__ = {"bSortable": False}

    def format(self, item):
        return item.language.iso_code

    def search(self, qs):
        return and_(Identifier.type.__eq__(IdentifierType.iso.value),
                    icontains(Identifier.name, qs))


class Dictionaries(Contributions):
    def __init__(self, *args, **kw):
        Contributions.__init__(self, *args, **kw)
        self.roles = {}
        for roleid in ROLES.keys():
            self.roles[roleid] = aliased(ContributionContributor, name='role%s' % roleid)

    def base_query(self, query):
        q = DBSession.query(Contribution)\
            .join(Dictionary.language)\
            .outerjoin(LanguageIdentifier)\
            .outerjoin(Identifier)\
            .outerjoin(IdsLanguage.family)\
            .options(
                contains_eager(Dictionary.language),
                joinedload(Dictionary.language, IdsLanguage.family))
        for roleid, alias in self.roles.items():
            q.join(alias, alias.ord == roleid)
        return q.distinct()

    def col_defs(self):
        res = [
            LinkCol(self, 'name'),
            LinkToMapCol(self, 'm', get_object=lambda i: i.language),
            IdsGlottocodeCol(self, 'Glottocode', get_object=lambda i: i.language),
            IdsISOCol(self, 'ISO', get_object=lambda i: i.language, sTitle='ISO 639-3'),
            MacroareaCol(self, 'macroarea', get_object=lambda i: i.language, language_cls=IdsLanguage),
            IdsFamilyCol(self, 'family', get_object=lambda i: i.language, language_cls=IdsLanguage),
        ]
        for roleid in ROLES.keys():
            res.append(ContributorCol(self, 'role%s' % roleid, roleid))
        res.append(CitationCol(self, 'cite'))
        return res


class ConcepticonLinkCol(Col):
    def format(self, item):
        return item.concepticon_link(self.dt.req)


class Entries(Parameters):
    __constraints__ = [Chapter]

    def base_query(self, query):
        query = query.join(Chapter)
        if self.chapter:
            query = query.filter(Chapter.pk == self.chapter.pk)
        return query

    def col_defs(self):
        return list(filter(lambda col: not self.chapter or col.name != 'sf', [
            IDSCodeCol(self, 'ids_code'),
            LinkCol(
                self, 'name', sTitle='Meaning',
                sDescription="This column shows the labels of the Loanword Typology "
                "meanings. By clicking on a meaning label, you get more information "
                "about the meaning, as well as a list of all words that are counterparts "
                "of that meaning."),
            ChapterCol(self, 'sf', sTitle='Chapter'),
            Col(self, 'representation', model_col=Entry.representation),
            ConcepticonLinkCol(self, 'concepticon', model_col=Entry.concepticon_gloss),
        ]))


class IDSSources(Sources):
    def base_query(self, query):
        return query.join(Provider)

    def get_options(self):
        opts = super(Sources, self).get_options()
        opts["aaSorting"] = [[1, "asc"]]
        return opts

    def col_defs(self):
        return [
            DetailsRowLinkCol(self, 'd'),
            LinkCol(self, 'name'),
            LinkCol(self, 'id', get_obj=lambda i: i.provider, sTitle='Dataset', model_col=Provider.name),
            Col(self, 'description', sTitle='Title', format=lambda i: HTML.span(i.description)),
            Col(self, 'year'),
            Col(self, 'author'),
            TypeCol(self, 'bibtex_type'),
        ]


class Chapters(DataTable):
    def col_defs(self):
        return [
            IntegerIdCol(self, 'id'),
            LinkCol(self, 'name'),
            Col(self, 'count_entries', sTitle='# Entries')
        ]


class Providers(DataTable):
    def get_options(self):
        opts = super(DataTable, self).get_options()
        opts["aaSorting"] = []
        return opts

    def col_defs(self):
        return [
            LinkCol(self, 'name'),
            ExternalLinkCol(self, 'url', sTitle='URL'),
            DetailsRowLinkCol(self, 'd'),
        ]


def includeme(config):
    config.register_datatable('chapters', Chapters)
    config.register_datatable('providers', Providers)
    config.register_datatable('values', Counterparts)
    config.register_datatable('contributors', Compilers)
    config.register_datatable('contributions', Dictionaries)
    config.register_datatable('parameters', Entries)
    config.register_datatable('sources', IDSSources)
