# this is to drive the final/more polished version of ofjustpy renderer
import ofjustpy as oj
import mistletoe
import md_view_handlers
app = oj.load_app()
md_input = "sample.md" #'example_all.md'
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


