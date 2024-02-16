import os
import logging
from addict import Dict
if os:
    try:
        os.remove("/tmp/launcher.log")
    except:
        pass

import sys
if sys:

    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(filename="/tmp/launcher.log",
                        level=logging.DEBUG, format=FORMAT)
    logger = logging.getLogger(__name__)

    
import ofjustpy as oj
import mistletoe
import md_view_handlers
app = oj.load_app()
#md_input = "headings.md"
md_input = 'example_all.md'
#md_input = "turn_on_off_view_directive.md"
with open(md_input, 'r') as fin:
    rendered = mistletoe.markdown(fin,
                                  mistletoe.OfjustpyRenderer,
                                  mditem_viewer_handlers=md_view_handlers
                                  )


wp_endpoint = oj.create_endpoint(key="mdviewer",
                                         childs = [rendered
                                                   ]
                                         )
oj.add_jproute("/", wp_endpoint)

