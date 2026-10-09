import pathlib
import argparse
import subprocess
from typing import Any

import git
from clldutils import jsonlib
from clldutils.path import Path
from clldutils.misc import slug
from cldfzenodo import API as ZenodoAPI


def prepare_additional_datasets(
        args: argparse.Namespace,
        submissions_path: pathlib.Path,
        cache_dir: pathlib.Path,
) -> dict[str, Any]:
    """Download and prepare resp. additional datasets"""
    rdfids = {}
    contrib_paths_map = {}
    contrib_repos = {}
    contrib_dois = {}
    contrib_skips = []
    contrib_order = {}
    unique_sids = set()
    unique_order = set()
    for contrib_dir in submissions_path.iterdir():
        if not contrib_dir.is_dir():
            continue

        args.log.info('Loading submission %s', contrib_dir.name)
        contrib_md = jsonlib.load(contrib_dir / 'md.json')
        sid = contrib_md['id']
        if sid in unique_sids:
            args.log.error('Id "%s" of %s is already used', sid, contrib_dir.name)
            assert False, 'id error'
        else:
            unique_sids.add(sid)

        order = int(contrib_md['order'])
        if order in unique_order:
            args.log.error('Order "%s" of %s is already used', sid, contrib_dir.name)
            assert False, 'order error'
        else:
            unique_order.add(order)

        rdfids[sid] = sid

        if contrib_md.get('skip') and contrib_md['skip']:
            contrib_skips.append(sid)
            args.log.info('   will be skipped')
            continue

        contrib_order[sid] = order

        if contrib_md.get('doi'):
            doi = contrib_md['doi']
            contrib_dois[sid] = doi
            int_id = '{}-{}'.format(sid, slug(doi))
            path = cache_dir / int_id
            if not path.exists():
                args.log.info(' * downloading dataset from Zenodo; doi: {0}'.format(doi))
                ZenodoAPI.get_record(doi=doi).download(path)
            else:
                args.log.info('   using cache')
            contrib_paths_map[int_id] = sid

        elif contrib_md.get('repo'):
            repo = contrib_md.get('repo')
            contrib_repos[sid] = repo
            # latest commit on the default branch
            path = cache_dir / sid
            if not path.exists():
                args.log.info(' * cloning {0} into {1}'.format(repo, path))
                git.Git().clone(repo, path)
            else:
                args.log.info(' * pulling latest commit')
                git.Git(str(path)).pull()
            contrib_paths_map[sid] = sid

        else:
            path = cache_dir / sid
            contrib_paths_map[sid] = sid

        if not path.exists():
            args.log.error('could not find folder', str(path))
            continue

    return {
        'rdfids': rdfids,
        'contrib_paths_map': contrib_paths_map,
        'contrib_repos': contrib_repos,
        'contrib_dois': contrib_dois,
        'contrib_skips': contrib_skips,
        'contrib_order': contrib_order,
    }


def get_rdfID(ds, ds_metadata, args):
    if ds.directory.parent.name in ds_metadata['contrib_paths_map']:
        ds_dir = ds_metadata['contrib_paths_map'][ds.directory.parent.name]
    else:
        args.log.warn('{0} was skipped due to unknown contrib_path'.format(
            ds.directory.parent.name))
        return None
    if ds_dir in ds_metadata['rdfids']:
        rdfID = ds_metadata['rdfids'][ds_dir]
    else:
        args.log.warn('{0} will be skipped - no "id" given'.format(ds_dir))
        return None
    return rdfID


def git_last_commit_date(dir_, git_command='git'):
    dir_ = Path(dir_)
    if not dir_.exists():
        raise ValueError('cannot read from non-existent directory')
    dir_ = dir_.resolve()
    cmd = [
        git_command,
        '--git-dir={0}'.format(dir_.joinpath('.git')),
        '--no-pager', 'log', '-1', '--format="%ai"'
    ]
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if p.returncode == 0:
            res = stdout.strip()  # pragma: no cover
        else:
            raise ValueError(stderr)
    except (ValueError, FileNotFoundError):
        return ''
    if not isinstance(res, str):
        res = res.decode('utf8')
    return res.replace('"', '')
