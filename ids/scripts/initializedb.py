import unicodedata
from itertools import groupby
from collections import defaultdict, OrderedDict
from datetime import date

import transaction
from sqlalchemy import Index
from sqlalchemy.orm import joinedload
from tqdm import tqdm

from clld.cliutil import Data, bibtex2source
from clld.db.meta import DBSession
from clld.db.models import common
from clld.db.util import collkey, with_collkey_ddl
from clld.lib.bibtex import Database
from clldutils.misc import slug, nfilter
from clldutils.path import Path
from clld_glottologfamily_plugin.util import load_families
from pyconcepticon.api import Concepticon
from pycldf.dataset import Wordlist, iter_datasets

import ids
from ids import models


CONCEPT_LIST = 'Key-2016-1310'

EDITORS = OrderedDict([
    ('maryritchiekey', ("Mary Ritchie Key", "University of California, Irvine")),
    ('bernardcomrie', ("Bernard Comrie", "University of California, Santa Barbara")),
])
with_collkey_ddl()


def main(args):
    data_set_path = input('Path to IDS cldf datasets:') or \
                    Path(ids.__file__).parent.parent.parent.parent / 'intercontinental-dictionary-series'
    ids_datasets = sorted(
        [ds for ds in iter_datasets(data_set_path)
         if ds.properties.get('dc:format', ['x'])[0].endswith(CONCEPT_LIST)],
        key=lambda d: (d.properties.get('rdf:ID') != 'ids', d.properties.get('rdf:ID')))
    assert ids_datasets and ids_datasets[0].properties['rdf:ID'] == 'ids', 'invalid ds directory'
    assert args.glottolog, 'The --glottolog option is required!'
    assert args.concepticon, 'The --concepticon option is required!'

    Index('ducet', collkey(common.Value.name)).create(DBSession.bind)
    data = Data()
    concept_list = {
        c.concepticon_id: c
        for c in Concepticon(args.concepticon).conceptlists[CONCEPT_LIST].concepts.values()}

    dataset = common.Dataset(
        id=ids.__name__,
        name="IDS",
        description="The Intercontinental Dictionary Series",
        published=date(2015, 5, 25),
        publisher_name="Max Planck Institute for Evolutionary Anthropology",
        publisher_place="Leipzig",
        publisher_url="https://www.eva.mpg.de",
        license='https://creativecommons.org/licenses/by/4.0/',
        contact='forkel@shh.mpg.de',
        jsondata={
            'license_icon': 'cc-by.png',
            'license_name':
                'Creative Commons Attribution 4.0 International License',
        },
        domain='ids.clld.org')

    DBSession.add(dataset)
    for ds in ids_datasets:
        for rec in Database.from_file(ds.bibpath, lowercase=True):
            if rec.id not in data['Source']:
                data.add(common.Source, rec.id, _obj=bibtex2source(rec))
    DBSession.flush()

    contributors = defaultdict(list)
    languages = []
    altnames = {}

    for ads in ids_datasets:
        for lg in ads["LanguageTable"]:
            lang = data.add(
                models.IdsLanguage,
                lg['ID'],
                id=lg['ID'],
                name=lg['Name'],
                latitude=lg['Latitude'],
                longitude=lg['Longitude'],
            )
            code = lg['Glottocode']
            if code:
                languages.append((code, lang))
            data.add(
                models.Dictionary,
                lg['ID'],
                id=lg['ID'],
                name=unicodedata.normalize('NFD', lg['Name']),
                language=lang,
                default_representation=lg['Representations'][0]
                if len(lg['Representations']) > 0 else None,
                alt_representation=lg['Representations'][1]
                if len(lg['Representations']) > 1 else None,
                jsondata=dict(status=0, date=lg['date']),
            )
            for idx, header in models.ROLES.items():
                for name in lg[header[1]]:
                    contributors[slug(name)].append((name, idx, lg['ID']))

            for i, an in enumerate(lg['alt_names']):
                if an in altnames:
                    identifier = altnames[an]
                else:
                    identifier = data.add(
                        common.Identifier, an,
                        id='name-%s' % i, type='name', name=an, description='IDS')
                    altnames[an] = identifier
                if an != data['IdsLanguage'][lg['ID']].name:
                    DBSession.add(common.LanguageIdentifier(
                        identifier=identifier,
                        language=data['IdsLanguage'][lg['ID']]))

    load_families(
        Data(),
        languages,
        glottolog_repos=args.glottolog,
        strict=False,
        isolates_icon='tcccccc',
    )

    for s, roles in contributors.items():
        name = roles[0][0]
        c = data.add(common.Contributor, s, id=s, name=name)
        if s in EDITORS:
            c.address = EDITORS[s][1]
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

    for i, (sid, (name, address)) in enumerate(EDITORS.items()):
        c = data['Contributor'].get(sid)
        if not c:
            c = data.add(common.Contributor, sid, id=sid, name=name, address=address)
        common.Editor(dataset=dataset, contributor=c, ord=i + 1)

    for c in ids_datasets[0]["chapters.csv"]:
        data.add(models.Chapter, c['ID'], id=c['ID'], name=c['Description'])

    for p in ids_datasets[0]["ParameterTable"]:
        chap_id, sub_id = p['ID'].split('-')
        data.add(
            models.Entry,
            p['ID'],
            id=p['ID'],
            name=p['Name'],
            concepticon_id=p['Concepticon_ID'],
            chapter_pk=int(chap_id),
            sub_code=sub_id,
            **{tr: concept_list[p['Concepticon_ID']].attributes[tr]
                for tr in 'french russian spanish portuguese'.split()},
        )

    DBSession.flush()
    for entity in 'IdsLanguage Entry Chapter Dictionary Source'.split():
        for k in list(data[entity].keys()):
            data[entity][k] = data[entity][k].pk

    DBSession.flush()

    synsets = {}
    counterparts = {}
    problems = defaultdict(list)

    for ds in ids_datasets:
        for lg_id, entries in tqdm(
            groupby(
                sorted(ds["FormTable"], key=lambda t: t['Language_ID']),
                lambda k: k['Language_ID']),
            desc='Loading words per dictionary in {}'.format(ds.properties.get('rdf:ID'))
        ):
            # keep the memory footprint reasonable
            transaction.commit()
            transaction.begin()

            language = common.Language.get(data['IdsLanguage'][lg_id])
            words = defaultdict(list)
            alt_repr, desc = '', ''
            for i, e in enumerate(entries):
                # all entries have the same sources/descriptions per lang
                if not i:
                    alt_repr = e['Transcriptions'][1]\
                        if len(e['Transcriptions']) > 1 else None
                    desc = e['Transcriptions'][0]\
                        if len(e['Transcriptions']) > 0 else None
                    if e['Source']:
                        for s in e['Source']:
                            DBSession.add(common.ContributionReference(
                                contribution_pk=language.pk, source_pk=data['Source'][s]))

                entry_id = e['Parameter_ID']
                id_ = '{0}-{1}'.format(entry_id, e['Language_ID'])
                try:
                    _ = synsets[id_]
                    vs = models.Synset.get(id_)
                except KeyError:
                    vs = models.Synset(
                        id=id_,
                        alt_representation=alt_repr,
                        language=language,
                        contribution_pk=data['Dictionary'][e['Language_ID']],
                        parameter_pk=data['Entry'][entry_id])
                    synsets[id_] = None

                word = e['Form']
                cid = '{0}-{1}'.format(
                    id_, str(int(e['ID'].split('-')[-1]) + 1 + len(vs.values)))
                try:
                    _ = counterparts[cid]
                except KeyError:
                    v = models.Counterpart(
                        id=cid,
                        name=word,
                        description=desc,
                        comment=e['Comment'],
                        org_value=e['Value'],
                        valueset=vs)
                    if e['AlternativeValues'] and e['AlternativeValues'][0]:
                        words[word].append((v, e['AlternativeValues'][0]))
                    else:
                        words[word].append((v, None))
                    counterparts[cid] = None

            for i, form in enumerate(words.keys()):
                # We identify words based on their string representation, and we can check
                # whether a word has the same alternative transcription for all meanings.
                # An alternative transcription can of course differ for the same string
                # representation (as in English [StandardOrth - IPA]: (to) present versus
                # (the) present).
                alt_names = nfilter(set(w[1] or '' for w in words[form]))
                try:
                    assert len(alt_names) <= 1
                except AssertionError:
                    problems[(language.id, language.name)].append(alt_names)
                word = models.Word(
                    id='{0}-{1}'.format(language.id, i + 1),
                    name=form,
                    description=desc,
                    language=language,
                    alt_name=', '.join(alt_names) if alt_names else None,
                    alt_description=alt_repr,
                )
                for v, _ in words[form]:
                    word.counterparts.append(v)
                DBSession.add(word)

            DBSession.flush()

    #if len(problems):
    #    print("=== Problems ===")
    #    for k, v in problems.items():
    #        print(k, v)


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodiucally whenever data has been updated.
    """
    for chapter in DBSession.query(models.Chapter).options(joinedload(models.Chapter.entries)):
        chapter.count_entries = len(chapter.entries)

    for entry in DBSession.query(models.Entry).options(joinedload(common.Parameter.valuesets)):
        entry.representation = len(entry.valuesets)
