import unicodedata
import re
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
import pycldf

import ids
from ids import models
from ids.scripts.utils.helper import git_last_commit_date, prepare_additional_datasets, get_rdfID


IDS_RDFID = 'ids'
CONCEPT_LIST = 'Key-2016-1310'

EDITORS = OrderedDict([
    ('maryritchiekey', ("Mary Ritchie Key", "University of California, Irvine")),
    ('bernardcomrie', ("Bernard Comrie", "University of California, Santa Barbara")),
])
with_collkey_ddl()


def main(args):

    # path of datasets
    internal_repo = Path(ids.__file__).parent.parent.parent.parent / 'intercontinental-dictionary-series' / 'ids-internal'

    assert args.glottolog, 'The --glottolog option is required!'
    assert args.concepticon, 'The --concepticon option is required!'

    cache_dir = internal_repo / 'datasets'
    cache_dir.mkdir(exist_ok=True)

    submissions_path = internal_repo / 'submissions-internal'

    ds_metadata = prepare_additional_datasets(args, submissions_path, cache_dir)

    is_ids_ds_found = False
    ids_datasets = [None] * max(ds_metadata['contrib_order'].values())

    # add all datasets by passed 'order' and ignore datasets marked as 'skip'
    for ds in pycldf.iter_datasets(cache_dir):
        if str(ds.directory).endswith('/cldf'):
            ds_dir = ds_metadata['contrib_paths_map'].get(ds.directory.parent.name, ds.directory.parent.name)
            if ds_dir in ds_metadata['contrib_skips']:
                if ds_metadata['contrib_skips'][ds_dir]:
                    args.log.info('{0} will be skipped'.format(ds_dir))
                    continue
            if ds_dir == IDS_RDFID:
                is_ids_ds_found = True
            ids_datasets[ds_metadata['contrib_order'][ds_dir] - 1] = ds
    ids_datasets = [x for x in ids_datasets if x is not None]

    assert is_ids_ds_found, 'dataset "ids" must be imported'

    Index('ducet', collkey(common.Value.name)).create(DBSession.bind)
    data = Data()
    concept_list = {
        c.concepticon_id: c
        for c in Concepticon(args.concepticon).conceptlists[CONCEPT_LIST].concepts.values()}

    dataset = common.Dataset(
        id=ids.__name__,
        name="IDS",
        description="The Intercontinental Dictionary Series",
        published=date(2021, 10, 4),
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
    DBSession.flush()

    contributors = defaultdict(list)
    languages = []
    altnames = {}
    max_lang_id = -1
    lang_id_map = defaultdict(dict)

    for ds in ids_datasets:
        rdfID = get_rdfID(ds, ds_metadata, args)
        if rdfID is None:
            continue

        doi = ''
        git_version = ''
        accessURL = ds.properties.get('dcat:accessURL')
        if rdfID in ds_metadata['contrib_dois']:
            doi = ds_metadata['contrib_dois'][rdfID]
            accessURL = 'https://doi.org/{0}'.format(doi)
        else:
            git_version = git_last_commit_date(ds.directory.parent)

        descr = ds.properties.get('dc:bibliographicCitation')
        if rdfID != IDS_RDFID:
            # remove possible 'Available online at ...' string
            # which will be added by IDS app on-the-fly
            descr = re.sub(r'\s*\(Available[^(]+?\)\s*$', '', descr),

        prov = data.add(
            models.Provider,
            rdfID,
            id=rdfID,
            name=ds.properties.get('dc:title'),
            description=descr,
            url=ds.properties.get('dc:identifier'),
            license=ds.properties.get('dc:license'),
            aboutUrl=ds.properties.get('aboutUrl'),
            accessURL=accessURL,
            version=git_version,
            doi=doi,
        )
        DBSession.flush()

        for rid, rec in enumerate(Database.from_file(ds.bibpath, lowercase=True)):
            rec_id = rec.id
            # set data url to accessURL and add Provider
            if rec_id not in data['IdsSource']:
                ns = bibtex2source(rec, models.IdsSource)
                if rdfID != IDS_RDFID and not ns.url:
                    ns.url = accessURL
                ns.id = rec_id
                ns.provider_pk = prov.pk
                src = data.add(
                    models.IdsSource,
                    rec_id,
                    _obj=ns,
                )
        DBSession.flush()

        for lg in ds["LanguageTable"]:
            # add additional language IDs after importing
            # IDS core as numbers
            if rdfID != IDS_RDFID:
                max_lang_id += 1
                lg_id = str(max_lang_id)
            else:
                lg_id = lg["ID"]
                if int(lg_id) > max_lang_id:
                    max_lang_id = int(lg_id)

            lang = data.add(
                models.IdsLanguage,
                lg_id,
                id=lg_id,
                name=lg['Name'],
                latitude=lg['Latitude'],
                longitude=lg['Longitude'],
            )

            lang_id_map[rdfID][lg["ID"]] = lg_id

            code = lg['Glottocode']
            if code:
                languages.append((code, lang))
            data.add(
                models.Dictionary,
                lg_id,
                id=lg_id,
                name=unicodedata.normalize('NFD', lg['Name']),
                language=lang,
                default_representation=lg['Representations'][0]
                if len(lg['Representations']) > 0 else None,
                alt_representation=';'.join(lg['Representations'][1:])
                if len(lg['Representations']) > 1 else None,
                jsondata=dict(status=0, date=lg['date']),
                provider_pk=prov.pk,
            )
            for idx, header in models.ROLES.items():
                for name in lg[header[1]]:
                    contributors[slug(name)].append((name, idx, lg_id))

        DBSession.flush()

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
            concepticon_gloss=concept_list[p['Concepticon_ID']].concepticon_gloss,
            concepticon_concept_id=concept_list[p['Concepticon_ID']].id,
            **{tr: concept_list[p['Concepticon_ID']].attributes[tr]
                for tr in 'french russian spanish portuguese'.split()},
        )

    DBSession.flush()
    for entity in 'IdsLanguage Entry Chapter Dictionary IdsSource'.split():
        for k in list(data[entity].keys()):
            data[entity][k] = data[entity][k].pk

    DBSession.flush()

    synsets = {}
    counterparts = {}
    problems = defaultdict(list)

    for ds in ids_datasets:
        rdfID = get_rdfID(ds, ds_metadata, args)
        if rdfID is None:
            continue

        for lg_id_, entries in tqdm(
            groupby(
                sorted(ds["FormTable"], key=lambda t: t['Language_ID']),
                lambda k: k['Language_ID']),
            desc='Loading words per dictionary in {}'.format(ds.properties.get('rdf:ID'))
        ):
            # keep the memory footprint reasonable
            transaction.commit()
            transaction.begin()

            lg_id = lang_id_map[rdfID][lg_id_]

            language = common.Language.get(data['IdsLanguage'][lg_id])
            words = defaultdict(list)
            alt_repr, desc = '', ''
            for i, e in enumerate(entries):
                # all entries have the same sources/descriptions per lang
                if not i:
                    alt_repr = e['Transcriptions'][1:]\
                        if len(e['Transcriptions']) > 1 else None
                    desc = e['Transcriptions'][0]\
                        if len(e['Transcriptions']) > 0 else None
                    if e['Source']:
                        for s in e['Source']:
                            DBSession.add(common.ContributionReference(
                                contribution_pk=language.pk, source_pk=data['IdsSource'][s]))

                entry_id = e['Parameter_ID']
                id_ = '{0}-{1}'.format(entry_id, lg_id)
                try:
                    _ = synsets[id_]
                    vs = models.Synset.get(id_)
                except KeyError:
                    vs = models.Synset(
                        id=id_,
                        alt_representation=';'.join(alt_repr) if alt_repr else None,
                        language=language,
                        contribution_pk=data['Dictionary'][lg_id],
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
                    if e['AlternativeValues'] and len(e['AlternativeValues']) > 0:
                        avs = ['' if v is None else v.strip() for v in e['AlternativeValues']]
                        words[word].append((v, ';'.join(avs)))
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
                    alt_description=';'.join(alt_repr) if alt_repr else None,
                )
                for v, _ in words[form]:
                    word.counterparts.append(v)
                DBSession.add(word)

        DBSession.flush()

    # if len(problems):
    #     print("=== Problems ===")
    #     for k, v in problems.items():
    #         print(k, v)


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodiucally whenever data has been updated.
    """
    for chapter in DBSession.query(models.Chapter).options(joinedload(models.Chapter.entries)):
        chapter.count_entries = len(chapter.entries)

    for entry in DBSession.query(models.Entry).options(joinedload(common.Parameter.valuesets)):
        entry.representation = len(entry.valuesets)
