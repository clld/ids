from __future__ import unicode_literals
import sys

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
            'license_name': 'Creative Commons Attribution-NonCommercial-NoDerivs 2.0 Germany License'},
        domain='ids.clld.org')
    #
    # TODO: license! editors!
    #
    #http://creativecommons.org/licenses/by-nc-nd/2.0/de/deed.en

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
    missing = {}
    for l in read('ids'):
        if l.data_1 == "- -" or not l.data_1.strip():
            continue
        #entry_id	chap_id	lg_id	data_1	data_2
        entry_id = '%s-%s' % (l.chap_id, l.entry_id)
        if entry_id not in data['Entry']:
            if entry_id in missing:
                missing[entry_id] += 1
            else:
                missing[entry_id] = 1
            continue
        id_ = '%s-%s' % (entry_id, l.lg_id)
        vs = data.add(
            common.ValueSet, id_,
            id=id_,
            #name=l.data_1,
            language=data['Language'][l.lg_id],
            contribution=data['Dictionary'][l.lg_id],
            parameter=data['Entry'][entry_id])
        data.add(
            common.Value, id_,
            id=id_,
            name=l.data_1,
            description=l.data_2 if l.data_2 != 'NULL' else None,
            jsondata=dict(comment=l.comment if l.comment != 'NULL' else None),
            valueset=vs)

    print missing
    print len(missing)
    print sum(missing.values())
    # contributor lang_compilers/what_did
    # contribution
    # source



def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodiucally whenever data has been updated.
    """


if __name__ == '__main__':
    initializedb(create=main, prime_cache=prime_cache)
    sys.exit(0)
