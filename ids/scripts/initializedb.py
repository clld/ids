# coding: utf8
from __future__ import unicode_literals, print_function
import sys
import re
from itertools import groupby
from collections import defaultdict
from datetime import date

import transaction
from sqlalchemy import Index
from sqlalchemy.orm import joinedload

from clld.scripts.util import initializedb, Data, bibtex2source
from clld.db.meta import DBSession
from clld.db.models import common
from clld.db.util import collkey, with_collkey_ddl
from clld.lib.bibtex import Database
from clldutils import dsv
from clldutils.misc import slug, nfilter
from clldutils.path import Path
from clld_glottologfamily_plugin.util import load_families
from pyglottolog.api import Glottolog
from pyglottolog.util import languoids_path
from pyglottolog.languoids import walk_tree
from concepticondata.api import Concepticon

import ids
from ids import models
from ids.scripts.util import LANGS


empty = re.compile('(NULL|[\s\-]*)$')


def get_string(s):
    return '' if empty.match(s) else s


# we may have to map iso codes to glottocodes by hand, e.g. arc (imperial aramaic) doesn't
# exist in glottolog 2.7.


def split_counterparts(c):
    for word in re.split('\s*(?:,|;)\s*', c):
        word = word.strip()
        if word and word not in ['—', '––']:
            yield word


def norm(f, desc, lid):
    f_ = f.replace('-', '').lower()
    if desc == 'Phonemic':
        for k, v in [
            ('\u045b', 'h'),
            ('\u043e', 'o'),
            ('\u0445', 'x'),
            ('\u0435', 'e'),
            ('\u0430', 'a'),
        ]:
            f_ = f_.replace(k, v)
    if int(lid) in [160, 162, 532]:
        f_ = f_.replace('\u2019', '\u02bc')
    #if int(lid) in [27, 29]:
    #    f_ = f_.replace('\u02b7', 'w')
    return f_


with_collkey_ddl()
GLOTTOLOG_REPOS = Path(ids.__file__).parent.parent.parent.parent.joinpath(
    'glottolog3', 'glottolog')
CONCEPTICON_REPOS = Path(ids.__file__).parent.parent.parent.parent.joinpath(
    'concepticon', 'concepticon-data')


def main(args):
    Index('ducet', collkey(common.Value.name)).create(DBSession.bind)
    data = Data()
    concept_list = Concepticon(CONCEPTICON_REPOS).conceptlist('Key-2016-1310')

    def concepticon_id(ids_code):
        for item in concept_list:
            if item['IDS_ID'] == ids_code:
                return int(item['CONCEPTICON_ID']) if item['CONCEPTICON_ID'] else None

    def read(table):
        fname = args.data_file(table + '.all.csv')
        if not fname.exists():
            fname = args.data_file(table + '.csv')
        return list(dsv.reader(fname, namedtuples=True))

    dataset = common.Dataset(
        id=ids.__name__,
        name="IDS",
        description="The Intercontinental Dictionary Series",
        published=date(2015, 5, 25),
        publisher_name="Max Planck Institute for Evolutionary Anthropology",
        publisher_place="Leipzig",
        publisher_url="http://www.eva.mpg.de",
        license='http://creativecommons.org/licenses/by/4.0/',
        contact='forkel@shh.mpg.de',
        jsondata={
            'license_icon': 'cc-by.png',
            'license_name':
                'Creative Commons Attribution 4.0 International License',
        },
        domain='ids.clld.org')

    DBSession.add(dataset)

    for rec in Database.from_file(args.data_file('sources.bib'), lowercase=True):
        if rec.id not in data['Source']:
            data.add(common.Source, rec.id, _obj=bibtex2source(rec))
    DBSession.flush()

    data_desc = defaultdict(dict)
    for l in read('x_lg_data'):
        data_desc[l.lg_id][l.map_ids_data] = l.header

    # language lang
    iso_codes = {l.id: l.sil_code for l in read('sil_lang')}
    iso_codes = {l.lg_id: iso_codes[l.sil_id] for l in read('x_lg_sil')}
    languages = []

    exclude = []
    for l in read('lang'):
        if l.status == '1':
            exclude.append(l.lg_id)
            continue
        lang_changed = LANGS.get(int(l.lg_id), {})
        code = lang_changed.get('glotto') or lang_changed.get('iso') or iso_codes.get(l.lg_id)
        lang = data.add(models.IdsLanguage, l.lg_id, id=l.lg_id, name=lang_changed.get('name', l.lg_name))
        if code:
            languages.append((code, lang))
        data.add(
            models.Dictionary, l.lg_id,
            id=l.lg_id, name=l.lg_name,
            language=lang,
            default_representation=data_desc[l.lg_id].get('1'),
            alt_representation=data_desc[l.lg_id].get('2'),
            jsondata=dict(status=l.status, date=l.date))

    iso2glotto = {}
    for l in walk_tree(tree=languoids_path('tree', GLOTTOLOG_REPOS)):
        if l.iso:
            iso2glotto[l.iso] = l.id

    load_families(
        Data(), [(iso2glotto.get(c, c), l) for c, l in languages], glottolog=Glottolog(GLOTTOLOG_REPOS), isolates_icon='tcccccc')

    contributors = defaultdict(list)
    sources = defaultdict(list)
    for l in read('lang_compilers'):
        if l.lg_id in exclude:
            continue
        if l.name == "BIBIKO":
            continue
        #name	lg_id	what_did_id
        if int(l.what_did_id) in models.ROLES:
            contributors[slug(l.name)].append((l.name, int(l.what_did_id), l.lg_id))
        else:
            assert int(l.what_did_id) in [4, 395]
            sources[l.name].append(l.lg_id)

    for s, roles in contributors.items():
        name = roles[0][0]
        c = data.add(common.Contributor, s, id=s, name=name)
        if name == 'Mary Ritchie Key':
            c.address = 'University of California, Irvine'
        for lg, specs in groupby(sorted(roles, key=lambda r: r[2]), key=lambda r: r[2]):
            sroles = sorted(
                [s[1] for s in specs],
                reverse=True,
                key=lambda what: what + 2 if what == 2 else what)
            what = sroles[0]
            DBSession.add(common.ContributionContributor(
                contribution=data['Dictionary'][lg],
                contributor=c,
                ord=what,
                primary=what == 2))

    data.add(
        common.Contributor, 'bernardcomrie',
        id='bernardcomrie',
        name="Bernard Comrie",
        address="University of California, Santa Barbara")

    for i, editor in enumerate(['maryritchiekey', 'bernardcomrie']):
        common.Editor(dataset=dataset, contributor=data['Contributor'][editor], ord=i + 1)

    #for i, name in enumerate(sorted(sources.keys())):
    #    c = data.add(common.Source, name, id=str(i + 1), name=name, description=name)

    DBSession.flush()
    for name, lgs in sources.items():
        for _src in name.split(';'):
            src = data['Source'].get(_src.strip())
            if not src:
                print('-- missing source --', _src)
                raise ValueError
            for lg in lgs:
                if lg in exclude:
                    continue
                assert lg in data['Dictionary']
                DBSession.add(common.ContributionReference(
                    contribution_pk=data['Dictionary'][lg].pk, source_pk=src.pk))

    altnames = {}
    for i, l in enumerate(read('alt_names')):
        if l.name in altnames:
            identifier = altnames[l.name]
        else:
            identifier = data.add(
                common.Identifier, l.name,
                id='name-%s' % i, type='name', name=l.name, description='IDS')
            altnames[l.name] = identifier
        if l.lg_id not in exclude and l.name != data['IdsLanguage'][l.lg_id].name:
            DBSession.add(common.LanguageIdentifier(
                identifier=identifier,
                language=data['IdsLanguage'][l.lg_id]))

    # parameter chapter/entry
    for l in read('chapter'):
        data.add(models.Chapter, l.chap_id, id=l.chap_id, name=l.chap_title)

    entries = {}
    for l in read('entry'):
        id_ = '%s-%s' % (l.chap_id, l.entry_id)
        name = l.trans_english
        if name in entries:
            entries[name] += 1
            name = name + ' (%s)' % entries[name]
        else:
            entries[name] = 1
        kw = {
            'id': id_,
            'name': name,
            'concepticon_id': concepticon_id(id_),
            'chapter': data['Chapter'][l.chap_id]}
        for ll in 'french russian spanish portugese'.split():
            kw[ll] = getattr(l, 'trans_' + ll)
        data.add(models.Entry, id_, sub_code=l.entry_id, **kw)

    misaligned = []

    DBSession.flush()
    for entity in 'IdsLanguage Entry Chapter Dictionary'.split():
        for k in data[entity].keys()[:]:
            data[entity][k] = data[entity][k].pk

    synsets = set()
    counterparts = set()
    problems = defaultdict(list)

    for lg_id, entries in groupby(
            sorted(read('ids'), key=lambda t: t.lg_id), lambda k: k.lg_id):
        if lg_id in exclude or not lg_id:
            continue

        # keep the memory footprint reasonable
        transaction.commit()
        transaction.begin()

        language = common.Language.get(data['IdsLanguage'][lg_id])
        desc = data_desc.get(lg_id, {})
        words = defaultdict(list)
        for l in entries:
            if empty.match(l.data_1):
                continue

            entry_id = '%s-%s' % (l.chap_id, l.entry_id)
            if entry_id not in data['Entry']:
                continue
                #data.add(
                #    models.Entry, entry_id,
                #    id=entry_id,
                #    name=entry_id,
                #    concepticon_id=concepticon_id(entry_id),
                #    sub_code=l.entry_id,
                #    chapter_pk=data['Chapter'][l.chap_id])
                #DBSession.flush()
                #data['Entry'][entry_id] = data['Entry'][entry_id].pk

            id_ = '%s-%s' % (entry_id, l.lg_id)
            if id_ in synsets:
                vs = models.Synset.get(id_)
            else:
                vs = models.Synset(
                    id=id_,
                    comment=get_string(l.comment or ''),
                    alt_representation=get_string(l.data_2),
                    language=language,
                    contribution_pk=data['Dictionary'][l.lg_id],
                    parameter_pk=data['Entry'][entry_id])
                synsets.add(id_)

            trans1 = list(split_counterparts(l.data_1))
            trans2 = None if empty.match(l.data_2) else list(split_counterparts(l.data_2))

            if trans2:
                if len(trans2) != len(trans1):
                    if language.id != '238':
                        misaligned.append((l.chap_id, l.entry_id, l.lg_id))
                        #print('===', language.id, language.name)
                        #print(l.data_1)
                        #print(l.data_2)
                    # 83 cases of misaligned transcriptions
                    trans2 = None

            for i, word in enumerate(trans1):
                cid = id_ + '-' + str(i + 1 + len(vs.values))
                if cid not in counterparts:
                    v = models.Counterpart(
                        id=cid,
                        name=word,
                        description=desc.get('1'),
                        valueset=vs)
                    words[word].append((v, trans2[i] if trans2 else None))
                    counterparts.add(cid)
                else:
                    print(cid)
                    #12 - 420 - 811 - 3
                    #5 - 390 - 818 - 3
                    #2 - 930 - 819 - 3
                    #2 - 930 - 819 - 3
                    #3 - 120 - 819 - 3
                    #10 - 140 - 822 - 3
                    #9 - 160 - 825 - 3
                    #2 - 430 - 829 - 4

        for i, form in enumerate(words.keys()):
            # Since we identify words based on their string representation, we have to
            # make sure a word has the same alternative transcription for all meanings.
            if language.id == '238':
                alt_names = []
            else:
                alt_names = set(norm(w[1] or '', desc.get('2'), language.id)
                                for w in words[form])
            alt_names = nfilter(alt_names)
            try:
                assert len(alt_names) <= 1
            except AssertionError:
                problems[(language.id, language.name)].append(alt_names)
            word = models.Word(
                id='%s-%s' % (language.id, i + 1),
                name=form,
                description=desc.get('1'),
                language=language,
                alt_name=', '.join(alt_names) if alt_names else None,
                alt_description=desc.get('2')
            )
            for v, _ in words[form]:
                word.counterparts.append(v)
            DBSession.add(word)

        DBSession.flush()

    with dsv.UnicodeWriter(args.data_file('misaligned.csv')) as fp:
        fp.writerows(misaligned)

    # about 250 cases where alternative transcriotions do not covary across meanings.
    for k, v in problems.items():
        print(k, len(v))


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodiucally whenever data has been updated.
    """
    for chapter in DBSession.query(models.Chapter).options(joinedload(models.Chapter.entries)):
        chapter.count_entries = len(chapter.entries)

    for entry in DBSession.query(models.Entry).options(joinedload(common.Parameter.valuesets)):
        entry.representation = len(entry.valuesets)


if __name__ == '__main__':
    initializedb(create=main, prime_cache=prime_cache)
    sys.exit(0)
