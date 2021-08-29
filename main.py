import asyncio
import os.path
import pkgutil
from collections import OrderedDict

import sys

import misc.plane
from pywebio.output import *
from pywebio.platform.tornado import start_server
from pywebio.session import *


def get_animation_modules():
    pkgpath = os.path.dirname(__file__)
    module_names = [m.name for m in pkgutil.walk_packages([pkgpath]) if not m.ispkg]
    module_names.sort()
    modules = OrderedDict()  # name -> module
    for m in module_names:
        try:
            __import__(m)
        except:
            continue
        module = sys.modules[m]
        if hasattr(module, 'frames'):
            modules[m] = module

    return modules


modules = get_animation_modules()


async def main():
    """ASCII Animations

    Animations created entirely out of text.
    """
    set_env(output_animation=False)

    module_name = (await eval_js("window.location.hash") or '')[1:]
    print(module_name)
    current_module = modules.get(module_name) or misc.plane
    changed = False

    def change_anim(module_name):
        nonlocal current_module, changed
        if module_name not in modules:
            return
        current_module = modules[module_name]
        changed = True
        with use_scope('title', clear=True):
            put_markdown('### %s' % current_module.name)
        run_js('window.location.hash="#%s"' % module_name)

    put_markdown("""## ASCII Animations
    Animations created entirely out of text. [Learn more about ASCII Animations](https://www.incredibleart.org/links/ascii.html).
    
    When viewing on cell phones, it is recommended to turn to landscape mode.
    
    The content is collected from the Internet. [Source code on Github](https://github.com/wang0618/ascii-art).
    """, strip_indent=4)

    put_buttons([
        (getattr(m, 'name', name), name)
        for name, m in modules.items()
    ], onclick=change_anim)

    with use_scope('title'):
        put_markdown('### %s' % current_module.name)

    set_scope('code')

    while 1:
        duration = getattr(current_module, 'duration', 100)
        for i in current_module.frames:
            with use_scope('code', clear=True):
                put_code(i.replace("\n\r", "\n"))
            await asyncio.sleep(duration / 1000.0)
            if changed:
                changed = False
                break


if __name__ == '__main__':
    start_server(main, port=8080)
