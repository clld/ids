from __future__ import unicode_literals, print_function
import sys
import re
from itertools import groupby
from collections import defaultdict
import transaction

from sqlalchemy import Index

from clld.scripts.util import initializedb, Data, glottocodes_by_isocode
from clld.db.meta import DBSession
from clld.db.models import common
from clld.db.util import collkey, with_collkey_ddl
from clld.lib import dsv
from clld.util import slug, nfilter

import ids
from ids import models


empty = re.compile('(NULL|[\s\-]*)$')


def get_string(s):
    return '' if empty.match(s) else s


def split_counterparts(c):
    for word in re.split('\s*(?:,|;)\s*', c):
        word = word.strip()
        if word:
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


def main(args):
    Index('ducet', collkey(common.Value.name)).create(DBSession.bind)
    glottocodes = glottocodes_by_isocode(
        #args.glottolog_dburi,
        'postgresql://robert@/glottolog3',
        cols='id latitude longitude'.split())
    data = Data()

    def read(table):
        return list(dsv.reader(
            args.data_file(table + '.csv'), delimiter=',', namedtuples=True))

    dataset = common.Dataset(
        id=ids.__name__,
        name="IDS",
        description="The Intercontinental Dictionary Series",
        #published=date(2009, 8, 15),
        publisher_name="Max Planck Institute for Evolutionary Anthropology",
        publisher_place="Leipzig",
        publisher_url="http://www.eva.mpg.de",
        license='http://creativecommons.org/licenses/by-nc-nd/2.0/de/deed.en',
        contact='ids@eva.mpg.de',
        jsondata={
            'license_icon': 'http://i.creativecommons.org/l/by-nc-nd/2.0/de/88x31.png',
            'license_name':
                'Creative Commons Attribution-NonCommercial-NoDerivs 2.0 Germany License',
        },
        domain='ids.clld.org')

    DBSession.add(dataset)
    data_desc = defaultdict(dict)
    for l in read('x_lg_data'):
        data_desc[l.lg_id][l.map_ids_data] = l.header

    # language lang
    exclude = []
    for l in read('lang'):
        if l.status == '1':
            exclude.append(l.lg_id)
            continue
        lang = data.add(common.Language, l.lg_id, id=l.lg_id, name=l.lg_name)
        data.add(
            models.Dictionary, l.lg_id,
            id=l.lg_id, name=l.lg_name,
            language=lang,
            default_representation=data_desc[l.lg_id].get('1'),
            alt_representation=data_desc[l.lg_id].get('2'),
            jsondata=dict(status=l.status, date=l.date))

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
            if int(l.what_did_id) not in [4, 395]:
                print(l.what_did_id)
                raise ValueError
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
        address="Max Planck Institute for Evolutionary Anthropology, Leipzig")

    for i, editor in enumerate(['maryritchiekey', 'bernardcomrie']):
        common.Editor(dataset=dataset, contributor=data['Contributor'][editor], ord=i + 1)

    for i, name in enumerate(sorted(sources.keys())):
        c = data.add(common.Source, name, id=str(i + 1), name=name, description=name)

    DBSession.flush()
    for name, lgs in sources.items():
        for lg in lgs:
            if lg in exclude:
                continue
            try:
                DBSession.add(common.LanguageSource(
                    language_pk=data['Language'][lg].pk,
                    source_pk=data['Source'][name].pk))
            except KeyError:
                print(name, lgs)
                continue

    # identifier sil_lang/alt_names
    for l in read('sil_lang'):
        data.add(
            common.Identifier, l.id,
            id='iso-%s' % l.id,
            type=common.IdentifierType.iso.value,
            name=l.sil_code,
            description=l.sil_name)
        if l.sil_code in glottocodes:
            gc = glottocodes[l.sil_code][0]
            data.add(
                common.Identifier, gc,
                id=gc,
                type=common.IdentifierType.glottolog.value,
                name=gc)

    altnames = {}
    for i, l in enumerate(read('alt_names')):
        if l.name in altnames:
            identifier = altnames[l.name]
        else:
            identifier = data.add(
                common.Identifier, l.name,
                id='name-%s' % i, type='name', name=l.name, description='IDS')
            altnames[l.name] = identifier
        if l.lg_id not in exclude and l.name != data['Language'][l.lg_id].name:
            DBSession.add(common.LanguageIdentifier(
                identifier=identifier,
                language=data['Language'][l.lg_id]))

    # languageidentifier x_lg_sil
    for l in read('x_lg_sil'):
        if l.lg_id in exclude:
            continue
        identifier = data['Identifier'][l.sil_id]
        language = data['Language'][l.lg_id]
        DBSession.add(common.LanguageIdentifier(identifier=identifier, language=language))
        if identifier.name in glottocodes:
            language.latitude = glottocodes[identifier.name][1]
            language.longitude = glottocodes[identifier.name][2]
            DBSession.add(common.LanguageIdentifier(
                identifier=data['Identifier'][glottocodes[identifier.name][0]],
                language=language))

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
        kw = {'id': id_, 'name': name, 'chapter': data['Chapter'][l.chap_id]}
        for ll in 'french russian spanish portugese'.split():
            kw[ll] = getattr(l, 'trans_' + ll)
        data.add(models.Entry, id_, sub_code=l.entry_id, **kw)

    misaligned = []

    DBSession.flush()
    for entity in 'Language Entry Chapter Dictionary'.split():
        for k in data[entity].keys()[:]:
            data[entity][k] = data[entity][k].pk

    synsets = set()

    for lg_id, entries in groupby(
            sorted(read('ids'), key=lambda t: t.lg_id), lambda k: k.lg_id):
        if lg_id in exclude or not lg_id:
            continue

        # keep the memory footprint reasonable
        transaction.commit()
        transaction.begin()

        try:
            language = common.Language.get(data['Language'][lg_id])
        except KeyError:
            print(list(entries))
            raise
        desc = data_desc.get(lg_id, {})
        words = defaultdict(list)
        for l in entries:
            if empty.match(l.data_1):
                continue

            entry_id = '%s-%s' % (l.chap_id, l.entry_id)
            if entry_id not in data['Entry']:
                data.add(
                    models.Entry, entry_id,
                    id=entry_id,
                    name=entry_id,
                    #active=False,
                    sub_code=l.entry_id,
                    chapter_pk=data['Chapter'][l.chap_id])
                DBSession.flush()
                data['Entry'][entry_id] = data['Entry'][entry_id].pk

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
                    #assert language.id == '238'  # Rapa Nui has problems!
                    trans2 = None

            for i, word in enumerate(trans1):
                v = models.Counterpart(
                    id=id_ + '-' + str(i + 1 + len(vs.values)),
                    name=word,
                    description=desc.get('1'),
                    valueset=vs)
                words[word].append((v, trans2[i] if trans2 else None))

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
                print('---', language.id, language.name)
                print(alt_names)
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


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodiucally whenever data has been updated.
    """
    # identify words:


if __name__ == '__main__':
    initializedb(create=main, prime_cache=prime_cache)
    sys.exit(0)
