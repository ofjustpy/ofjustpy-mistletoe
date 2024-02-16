import ofjustpy as oj

from py_tailwind_utils import *
from jsonpath_ng import jsonpath, parse

session_manager = None

def list_item(cgens, key_cursor):
    return oj.StackV_("blahblah", cgens=[])


def gridify():
    return oj.PC.StackG(num_cols=3, childs=[]) #mditem_data['list'])


#this is the default list item viwer
def para_as_span_viewer(mditem_data):
    """
    strip para and graph the rawText to define the span
    """

    print (mditem_data)
    jsonpath_expr = parse('$.list_item[0].para[0].rawText')
    span_text = [_.value for _ in jsonpath_expr.find(mditem_data)][0]
    print ('span_text = ', span_text)
    return oj.Span_("aspan", text =span_text)


#this is the default list item viwer
def href_image_viewer(mditem_data):
    jsonpath_expr = parse('$.list_item[0].para[0].ahref')
    _d  = [_.value for _ in jsonpath_expr.find(mditem_data)][0]
    jsonpath_expr = parse('$.list_item[0].para[2].img')
    _i = [_.value for _ in jsonpath_expr.find(mditem_data)][0]
    href = oj.PC.A(text= _d.desc, title = _d.title, href=_d.target)
    img = oj.PC.Img(src =_i.src, title = _d.title, alt=_d.desc, twsty_tags=[of.cn]) # 
    return oj.PC.StackV(childs=[href, img])




    
