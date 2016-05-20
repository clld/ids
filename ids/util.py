# coding: utf8
from __future__ import unicode_literals, print_function, division

from clld.db.meta import DBSession
from clld.db.models.common import Source, Parameter
from clld.web.util.helpers import get_referents
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


def concepticon_link(request, meaning):
    return HTML.a(
        HTML.img(
            src=request.static_url('ids:static/concepticon_logo.png'),
            height=20,
            width=30),
        title='corresponding concept set at Concepticon',
        href=meaning.concepticon_url)
