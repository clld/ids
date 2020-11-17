from sqlalchemy import Integer
from sqlalchemy.sql.expression import cast, func
from sqlalchemy.orm import aliased, joinedload, contains_eager

from clld.web.datatables import Values, Sources
from clld.web.datatables.base import Col, LinkCol, LinkToMapCol, DataTable, IntegerIdCol
from clld.web.datatables.contribution import Contributions, CitationCol
from clld.web.datatables import contributor
from clld.web.datatables.parameter import Parameters
from clld.web.util.helpers import link
from clld.web.util.htmllib import HTML
from clld.db.meta import DBSession
from clld.db.util import collkey
import clld.db.models.common
from clld.db.models.common import ValueSet, Value
from clld_glottologfamily_plugin.datatables import MacroareaCol, FamilyCol
from clld_glottologfamily_plugin.models import Family

from ids.models import Chapter, Entry, ROLES, Dictionary, IdsLanguage


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
        return collkey(func.replace(func.replace(Value.name, '`', ''), 'ː', ''))


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
                .join(Family, isouter=True)\
                .options(joinedload(Value.valueset).joinedload(ValueSet.language),
                         joinedload(Value.valueset, ValueSet.parameter))
        if self.contribution:
            return query
        return query.join(Family, isouter=True)

    def col_defs(self):
        lang = lambda i: i.valueset.language
        param = lambda i: i.valueset.parameter
        if self.parameter:
            res = [
                LinkToMapCol(self, 'm', get_object=lang),
                LinkCol(
                    self, 'language',
                    model_col=clld.db.models.common.Language.name,
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
                    model_col=clld.db.models.common.Parameter.id,
                    get_object=param),
                LinkCol(
                    self, 'meaning',
                    model_col=clld.db.models.common.Parameter.name,
                    get_object=param),
                ChapterCol(self, 'chapter', get_object=param)]
        else:
            res = [
                IDSCodeCol(
                    self, 'ids_code',
                    model_col=clld.db.models.common.Parameter.id,
                    get_object=param),
                LinkCol(
                    self, 'meaning',
                    model_col=clld.db.models.common.Parameter.name,
                    get_object=param),
                ChapterCol(self, 'chapter', get_object=param),
                LinkCol(
                    self, 'language',
                    model_col=clld.db.models.common.Language.name,
                    get_object=lang),
                IdsFamilyCol(
                    self, 'family',
                    language_cls=IdsLanguage,
                    get_object=lambda i: i.valueset.language),
            ]
        res.extend([
            FormCol(
                self, 'counterparts',
                model_col=clld.db.models.common.Value.name,
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
        return DBSession.query(clld.db.models.common.ContributionContributor).join(clld.db.models.common.Contribution).join(clld.db.models.common.Contributor)

    def col_defs(self):
        return [
            LinkCol(self, 'name', get_object=lambda i: i.contributor, model_col=clld.db.models.common.Contributor.name),
            RoleCol(self, 'role', model_col=clld.db.models.common.ContributionContributor.ord),
            LinkCol(self, 'dictionary', get_object=lambda i: i.contribution, model_col=clld.db.models.common.Contribution.name),
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


class Dictionaries(Contributions):
    def __init__(self, *args, **kw):
        Contributions.__init__(self, *args, **kw)
        self.roles = {}
        for roleid in ROLES.keys():
            self.roles[roleid] = aliased(clld.db.models.common.ContributionContributor, name='role%s' % roleid)

    def base_query(self, query):
        q = DBSession.query(clld.db.models.common.Contribution)\
            .join(Dictionary.language)\
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
    def get_options(self):
        opts = super(Sources, self).get_options()
        opts["aaSorting"] = [[1, "asc"]]
        return opts


class Chapters(DataTable):
    def col_defs(self):
        return [
            IntegerIdCol(self, 'id'),
            LinkCol(self, 'name'),
            Col(self, 'count_entries', sTitle='# Entries')
        ]


def includeme(config):
    config.register_datatable('chapters', Chapters)
    config.register_datatable('values', Counterparts)
    config.register_datatable('contributors', Compilers)
    config.register_datatable('contributions', Dictionaries)
    config.register_datatable('parameters', Entries)
    config.register_datatable('sources', IDSSources)
