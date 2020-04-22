import pathlib

from clld.web.assets import environment

import ids


environment.append_path(
    str(pathlib.Path(ids.__file__).parent.joinpath('static')), url='/ids:static/')
environment.load_path = list(reversed(environment.load_path))
