from clld.web.assets import environment
from path import path

import ids


environment.append_path(
    path(ids.__file__).dirname().joinpath('static'), url='/ids:static/')
environment.load_path = list(reversed(environment.load_path))
