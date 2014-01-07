from __future__ import unicode_literals
import sys
import re
import codecs
from itertools import groupby
from collections import defaultdict

from sqlalchemy import create_engine
from clld.scripts.util import initializedb, Data
from clld.db.meta import DBSession
from clld.db.models import common
from clld.lib import dsv
from clld.util import slug

import ids
from ids import models


GC = create_engine('postgresql://robert@/glottolog3')

glottocodes = {}
for row in GC.execute('select ll.hid, l.id, l.latitude, l.longitude from language as l, languoid as ll where ll.pk = l.pk'):
    if row[0] and len(row[0]) == 3:
        glottocodes[row[0]] = (row[1], row[2], row[3])


def split_counterparts(c):
    for word in re.split('\s*(?:\,|\;)\s*', c):
        word = word.strip()
        if word:
            yield word


def main(args):
    data = Data()

    def read(table):
        return list(dsv.rows(
            args.data_file(table + '.tsv'), namedtuples=True, encoding='utf8'))

    dataset = common.Dataset(
        id=ids.__name__,
        name="IDS",
        description="The Intercontinental Dictionary Series",
        #published=date(2009, 8, 15),
        license='http://creativecommons.org/licenses/by-nc-nd/2.0/de/deed.en',
        contact='ids@eva.mpg.de',
        jsondata={
            'license_icon': 'http://i.creativecommons.org/l/by-nc-nd/2.0/de/88x31.png',
            'license_name':
                'Creative Commons Attribution-NonCommercial-NoDerivs 2.0 Germany License',
        },
        domain='ids.clld.org')

    DBSession.add(dataset)

    # language lang
    for l in read('lang'):
        lang = data.add(common.Language, l.lg_id, id=l.lg_id, name=l.lg_name)
        data.add(
            models.Dictionary, l.lg_id,
            id=l.lg_id, name=l.lg_name,
            language=lang,
            jsondata=dict(status=l.status, date=l.date))

    ROLES = {
        '1': 'Data Entry',
        '2': 'Compiler',
        '3': 'Consultant',
    }

    contributors = {}
    sources = {}
    for l in read('lang_compilers'):
        if l.name == "BIBIKO":
            continue
        #name	lg_id	what_did_id
        if l.what_did_id in ['1', '2', '3']:
            s = slug(l.name)
            if s in contributors:
                contributors[s].append((l.name, l.what_did_id, l.lg_id))
            else:
                contributors[s] = [(l.name, l.what_did_id, l.lg_id)]
        else:
            if l.name in sources:
                sources[l.name].append(l.lg_id)
            else:
                sources[l.name] = [l.lg_id]

    for s, roles in contributors.items():
        name = roles[0][0]
        c = data.add(common.Contributor, s, id=s, name=name)
        if name == 'Mary Ritchie Key':
            c.address = 'University of California, Irvine'
        for _, what, lg in roles:
            DBSession.add(common.ContributionContributor(
                contribution=data['Dictionary'][lg],
                contributor=c,
                jsondata=dict(role=ROLES[what]),
                primary=what == '2'))

    data.add(
        common.Contributor, 'bernardcomrie',
        id='bernardcomrie',
        name="Bernard Comrie",
        address="Max Planck Institute for Evolutionary Anthropology, Leipzig")

    for i, editor in enumerate(['maryritchiekey', 'bernardcomrie']):
        common.Editor(dataset=dataset, contributor=data['Contributor'][editor], ord=i + 1)

    for i, name in enumerate(sources):
        c = data.add(common.Source, name, id=str(i + 1), name=name, description=name)

    DBSession.flush()
    for name, lgs in sources.items():
        for lg in lgs:
            try:
                DBSession.add(common.LanguageSource(
                    language_pk=data['Language'][lg].pk,
                    source_pk=data['Source'][name].pk))
            except KeyError:
                print name, lgs
                continue

    # identifier sil_lang/alt_names
    for l in read('sil_lang'):
        data.add(
            common.Identifier, l.id,
            id='iso-%s' % l.id, type=common.IdentifierType.iso.value, name=l.sil_code, description=l.sil_name)
        if l.sil_code in glottocodes:
            gc = glottocodes[l.sil_code][0]
            data.add(common.Identifier, gc, id=gc, type=common.IdentifierType.glottolog.value, name=gc)

    altnames = {}
    for i, l in enumerate(read('alt_names')):
        if l.name in altnames:
            identifier = altnames[l.name]
        else:
            identifier = data.add(
                common.Identifier, l.name,
                id='name-%s' % i, type='name', name=l.name, description='IDS')
            altnames[l.name] = identifier
        if l.name != data['Language'][l.lg_id].name:
            DBSession.add(common.LanguageIdentifier(
                identifier=identifier, language=data['Language'][l.lg_id]))

    # languageidentifier x_lg_sil
    for l in read('x_lg_sil'):
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

    # valueset
    # value ids
    data_desc = {}
    for l in read('x_lg_data'):
        if l.lg_id in data_desc:
            data_desc[l.lg_id][l.map_ids_data] = l.header
        else:
            data_desc[l.lg_id] = {l.map_ids_data: l.header}

    missing = {}
    empty = re.compile('(NULL|[\s\-]*)$')
    for lg_id, entries in groupby(sorted(read('ids'), key=lambda t: t.lg_id), lambda k: k.lg_id):
        language = data['Language'][lg_id]
        desc = data_desc.get(l.lg_id, {})
        words = defaultdict(list)
        for l in entries:
            if empty.match(l.data_1):
                continue
            #entry_id	chap_id	lg_id	data_1	data_2
            entry_id = '%s-%s' % (l.chap_id, l.entry_id)
            if entry_id not in data['Entry']:
                if entry_id in missing:
                    missing[entry_id].append((language.name, l.data_1))
                else:
                    missing[entry_id] = [(language.name, l.data_1)]
                continue

            id_ = '%s-%s' % (entry_id, l.lg_id)
            vs = common.ValueSet(
                id=id_,
                jsondata=dict(comment=l.comment if l.comment != 'NULL' else None),
                language=language,
                contribution=data['Dictionary'][l.lg_id],
                parameter=data['Entry'][entry_id])

            trans1 = split_counterparts(l.data_1)
            trans2 = None #if empty.match(l.data_2) else re.split('\s*(?:\,|\;)\s*', l.data_2)

            #if trans2:
            #    if len(trans2) != len(trans1):
            #        if language.id != '238':
            #            print language.id, language.name
            #            print l.data_1
            #            print l.data_2
            #        #assert language.id == '238'  # Rapa Nui has problems!
            #        trans2 = None

            for i, word in enumerate(trans1):
                v = models.Counterpart(
                    id=id_ + '-' + str(i + 1),
                    name=word,
                    #description=desc.get('1'),
                    valueset=vs)
                words[word].append((v, trans2[i] if trans2 else None))

        for i, form in enumerate(words.keys()):
            # make sure the word has the same alternative transcription for all meanings:
            #if language.id == '238':
            #    alt_names = []
            #else:
            #    alt_names = set((w[1] or '').replace('-', '') for w in words[word])
            #alt_names = filter(None, list(alt_names))
            #try:
            #    assert len(alt_names) <= 1
            #except AssertionError:
            #    print language.id, language.name
            #    print alt_names
            word = models.Word(
                id='%s-%s' % (language.id, i + 1),
                name=form,
                description=desc.get('1'),
                language=language,
                #alt_name=alt_names[0] if alt_names else None,
                #alt_description=desc.get('2')
            )
            for v, _ in words[form]:
                word.counterparts.append(v)
            DBSession.add(word)

        DBSession.flush()

    with codecs.open(args.data_file('missing.tsv'), 'w', encoding='utf8') as fp:
        for id_, items in missing.items():
            for l, c in items:
                fp.write('%s\t%s\t%s\n' % (id_, l, c))

    # contributor lang_compilers/what_did
    # contribution
    # source


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodiucally whenever data has been updated.
    """
    # identify words:


if __name__ == '__main__':
    initializedb(create=main, prime_cache=prime_cache)
    sys.exit(0)
