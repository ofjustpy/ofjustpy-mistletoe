import ofjustpy as oj
from py_tailwind_utils import of, pd, sl
from jsonpath_ng import jsonpath, parse


def gridify():
    # should be nested within a section
    return oj.PC.StackG(num_cols=3, childs=[], twsty_tags=[pd/sl/4]) #mditem_data['list'])


#this is the default list item viwer
def href_image_viewer(mditem_data):
    jsonpath_expr = parse('$.list_item[0].para[0].ahref')
    _d  = [_.value for _ in jsonpath_expr.find(mditem_data)][0]
    jsonpath_expr = parse('$.list_item[0].para[2].img')
    _i = [_.value for _ in jsonpath_expr.find(mditem_data)][0]
    href = oj.PC.A(text= _d.desc, title = _d.title, href=_d.target)
    img = oj.PC.Img(src =_i.src, title = _d.title, alt=_d.desc, width="140",  height="100", twsty_tags=[of.cn]) # 
    return oj.PC.StackV(childs=[href, img])
