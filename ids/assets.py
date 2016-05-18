from clld.web.assets import environment
from clldutils.path import Path

import ids


environment.append_path(
    Path(ids.__file__).parent.joinpath('static').as_posix(), url='/ids:static/')
environment.load_path = list(reversed(environment.load_path))
