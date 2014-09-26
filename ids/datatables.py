from sqlalchemy import Integer
from sqlalchemy.sql.expression import cast
from sqlalchemy.orm import aliased, joinedload

from clld.web.datatables import Values
from clld.web.datatables.base import Col, LinkCol, LinkToMapCol
from clld.web.datatables.contribution import Contributions, CitationCol
from clld.web.datatables import contributor
from clld.web.datatables.parameter import Parameters
from clld.web.util.helpers import link
from clld.web.util.htmllib import HTML
from clld.db.meta import DBSession
import clld.db.models.common

from ids.models import Chapter, Entry, ROLES, Dictionary


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


class Counterparts(Values):
    """Lists of counterparts
    """
    def col_defs(self):
        if self.parameter:
            lang = lambda i: i.valueset.language
            res = [
                LinkToMapCol(self, 'm', get_object=lang),
                LinkCol(
                    self, 'language',
                    model_col=clld.db.models.common.Language.name,
                    get_object=lang),
            ]
        else:
            param = lambda i: i.valueset.parameter
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
        res.extend([
            LinkCol(
                self, 'counterparts',
                model_col=clld.db.models.common.Value.name,
                sClass="charissil"),
            Col(self, 'description'),
        ])
        return res


class RoleCol(Col):
    __kw__ = {'choices': ROLES.items(), 'sClass': 'left'}

    def format(self, item):
        return ROLES[item.ord]


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
        kw['sTitle'] = ROLES[roleid]
        Col.__init__(self, dt, name, **kw)
        self.roleid = roleid

    def format(self, item):
        return HTML.ul(
            *[HTML.li(link(self.dt.req, ca.contributor))
              for ca in item.contributor_assocs if ca.ord == self.roleid])


class Dictionaries(Contributions):
    def __init__(self, *args, **kw):
        Contributions.__init__(self, *args, **kw)
        self.roles = {}
        for roleid in ROLES:
            self.roles[roleid] = aliased(clld.db.models.common.ContributionContributor, name='role%s' % roleid)

    def base_query(self, query):
        q = DBSession.query(clld.db.models.common.Contribution).options(joinedload(Dictionary.language))
        for roleid, alias in self.roles.items():
            q.join(alias, alias.ord == roleid)
        return q.distinct()

    def col_defs(self):
        res = [
            LinkCol(self, 'name'),
            LinkToMapCol(self, 'm', get_object=lambda i: i.language),
        ]
        for roleid in ROLES.keys():
            res.append(ContributorCol(self, 'role%s' % roleid, roleid))
        res.append(CitationCol(self, 'cite'))
        return res


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
        ]))


def includeme(config):
    config.register_datatable('values', Counterparts)
    config.register_datatable('contributors', Compilers)
    config.register_datatable('contributions', Dictionaries)
    config.register_datatable('parameters', Entries)
