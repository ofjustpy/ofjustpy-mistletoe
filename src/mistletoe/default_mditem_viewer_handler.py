import jsbeautifier
import ofjustpy as oj
from jsonpath_ng import jsonpath, parse
from py_tailwind_utils import bg, green, pink
def list_item_view_handler(li_data):
    """
    if list item contains only text then li_data would look as follows:
    {'list_item': [{'para': [{'rawText': 'text for input item 1'}]}]}
    """
    # we expect only one para for this metadata
    assert 'list_item' in li_data
    assert len(li_data['list_item']) == 1
    para = li_data['list_item'][0]['para']
    return oj.PC.Li(text=para[0]['rawText'])


def paragraph_view_handler(mditem_data):
    jsonpath_expr = parse('$.paragraph[0].rawText')
    para_text = [_.value for _ in jsonpath_expr.find(mditem_data)][0]
    return oj.PC.Prose(text=para_text)


def heading1_view_handler(mditem_data,  level, content_stub):
    """
    content_stub is required since heading is rendered as oj.Subsection_()
    mditem_data = {'heading': [{'rawText': 'Hello'}]}
    """
    jsonpath_expr = parse('$.heading[0].rawText')
    heading_text = [_.value for _ in jsonpath_expr.find(mditem_data)][0]
    return oj.PC.Subsubsection(heading_text, content_stub
                               )


def heading2_view_handler(mditem_data, level, content_stub):
    """
    content_stub is required since heading is rendered as oj.Subsection_()
    mditem_data = {'heading': [{'rawText': 'Hello'}]}
    """
    jsonpath_expr = parse('$.heading[0].rawText')
    heading_text = [_.value for _ in jsonpath_expr.find(mditem_data)][0]
    return oj.PC.TitledPara(heading_text,
                            content_stub,
                            fix_sty_section_nesting=True,
                            )

def heading3_view_handler(mditem_data, level, content_stub):
    """
    content_stub is required since heading is rendered as oj.Subsection_()
    mditem_data = {'heading': [{'rawText': 'Hello'}]}
    """
    jsonpath_expr = parse('$.heading[0].rawText')
    heading_text = [_.value for _ in jsonpath_expr.find(mditem_data)][0]
    return oj.PC.TitledPara(heading_text, content_stub, fix_sty_section_nesting=True)


def heading4_view_handler(mditem_data, level, content_stub):
    """
    content_stub is required since heading is rendered as oj.Subsection_()
    mditem_data = {'heading': [{'rawText': 'Hello'}]}
    """
    jsonpath_expr = parse('$.heading[0].rawText')
    heading_text = [_.value for _ in jsonpath_expr.find(mditem_data)][0]
    return oj.PC.TitledPara(heading_text,
                            content_stub,
                            fix_sty_section_nesting=True
                            )

    
