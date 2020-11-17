import unicodedata
import re
from clld.db.meta import DBSession
from clld.db.models.common import Source, Parameter
from clld.web.util.helpers import get_referents, link
from clld.web.util.htmllib import HTML

from ids.models import Chapter


def dataset_detail_html(context=None, request=None, **kw):
    return {
        'buck1949': Source.get('buck1949'),
        'entries': DBSession.query(Parameter).count(),
        'chapters': DBSession.query(Chapter).count(),
    }


def source_detail_html(context=None, request=None, **kw):
    return dict(
        referents=get_referents(context, exclude=['sentence', 'valueset', 'language']))


def parse_comment_for_meaning_links(request, comment, lg_id):
    comment = HTML.escape(comment)
    for c in re.findall(r'(\d+\.\d+)', comment):
        comment = comment.replace(
            c,
            link(
                request,
                '{0}-{1}'.format('-'.join([str(int(i)) for i in c.split('.')]), lg_id),
                rsc='valueset',
                label=c))
    return comment


def has_any_comments(values):
    return any([v.comment for v in values])


def has_same_comments(values):
    return len(set([v.comment for v in values])) > 0


def any_org_value_differ(values):
    return any(
        [unicodedata.normalize('NFD', v.org_value) != unicodedata.normalize('NFD', str(v.word))
            for v in values])


def has_same_org_values(values):
    return len(set([v.org_value for v in values])) > 0
