from .gui import init_gui, init_gui_with_h5parm

from typing import Union

def main(logger, h5parm: Union[str, None] = None):
    if h5parm is None:
        init_gui(logger)
    else:
        init_gui_with_h5parm(logger, h5parm)