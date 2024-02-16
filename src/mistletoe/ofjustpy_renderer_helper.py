import logging
import os
if os:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    
import functools
from addict import Dict
import ofjustpy as oj
import traceback
import sys
from typing import Any, NamedTuple
from py_tailwind_utils import W, pd, full, sl



# def captureViewDirective(func):
#     """
#     L6 headings are view directives; should be removed from rendering 
#     """
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         #logger.info("Capture view directive wrapper invoded")
        
#         renderer_obj = args[0]
#         token = args[1]
#         print("poking on L6 = ", renderer_obj, " ", token)
        
#         if token.level == 6:
#             renderer_obj.parsing_in_meta_mode = True
#             inner = [_ for _ in renderer_obj.render_inner(token) if _ is not None]
#             renderer_obj.parsing_in_meta_mode = False
#             view_directive = inner[0].rawText
#             handler_type, handler_funcname = view_directive.split(":")
#             if handler_funcname != 'None':
#                 renderer_obj.mditem_viewer_handler_map[handler_type] = renderer_obj.mdview_funclookup[handler_funcname]
#             else:
#                 logger.info(f"view directive: no handler associated with {handler_type} ")
#                 renderer_obj.mditem_viewer_handler_map[handler_type] = None

#             return
#         else:
#             return func(*args, **kwargs)

#     return wrapper

# all about context of mditems
ctx_depth = 0

class ctx(NamedTuple):
    ctxtype: Any
    ctxhandle: Any

def pop_covering_ctx(covering_ctx_stack, ctxtype):
    global ctx_depth
    last_ctx = covering_ctx_stack.pop()
    spaces = "".join([" " for i in range(ctx_depth)])
    #print (f"{spaces} </{last_ctx.ctxtype}>")
    ctx_depth -= 1
    while True:
        if not covering_ctx_stack:
            break
        if last_ctx.ctxtype == ctxtype:
            break
        last_ctx = covering_ctx_stack.pop()
        #spaces = "".join([" " for i in range(ctx_depth)])
        #print (f"{spaces} </{last_ctx.ctxtype}>")
        ctx_depth -= 1

def check_and_pop(covering_ctx_stack, ctxtype):
    needs_pop  = False
    # check if ctx appears earlier
    for ctxitem in covering_ctx_stack:
        if ctxitem.ctxtype == ctxtype:
            logger.debug(f"for {ctxtype}: pop is required")
            needs_pop = True

    if needs_pop:
        pop_covering_ctx(covering_ctx_stack, ctxtype)
        
def append_covering_ctx(covering_ctx_stack, ctxtype,  ctxhandle):
    """
    context_handle == None implies a closed context 
    """
    global ctx_depth
    #spaces = "".join([" " for i in range(ctx_depth)])
    #logger.debug(f"{spaces} new-covering-ctx: <", ctxtype, ">")
    covering_ctx_stack.append(ctx(ctxtype,  ctxhandle))
    ctx_depth += 1

        
def attach_to_covering_ctx(covering_ctx_stack, ref):
    top_ctx = covering_ctx_stack[-1]
    if top_ctx.ctxhandle is None:
        return ref
    else:
        top_ctx.ctxhandle.components.append(ref)
        return None

# def get_hcgen(func, renderer_obj):
#     mditem_name = func.__name__.replace("render_", "")
#     view_func_name = mditem_name + "_view_handler"

    
def openHeadingCtx(func, renderer_obj, token, *args, **kwargs):
    global ctx_depth

    mditem_ctxstack = renderer_obj.mditem_ctxstack
    mditem_name = func.__name__.replace("render_", "")
    if mditem_name == "heading":
        mditem_name += str(token.level)
    #hc_key = renderer_obj.get_key(f"{mditem_name}")
    #hc_container_key = renderer_obj.get_key(f"container_{mditem_name}")
    # create a subsection stub_
    
    # StackV holds all direct childs 
    content_stub = oj.PC.StackV(childs = [], twsty_tags=[W/full, pd/sl/4])
    check_and_pop(mditem_ctxstack,  mditem_name)
    parent_ctx = None
    if len(mditem_ctxstack) > 0:
        parent_ctx = mditem_ctxstack[-1]
    #spaces = " ".join([" " for _ in range(ctx_depth)])
    #ctx_depth +=1
    #logging.debug(f"{spaces} ================covering_ctx/{mditem_name}======")

    append_covering_ctx(mditem_ctxstack,  mditem_name,  content_stub)

    # prepare to call custom view handler
    # collect heading text
    res = func(*args,  **kwargs, asdict=True)
    #key = renderer_obj.get_key(mditem_name)
    view_func_name = mditem_name + "_view_handler"
    hcgen = renderer_obj.mditem_viewer_handler_map[view_func_name]
    # hcgen is the view_handler for heading<level>
    mditem_view_stub_ = hcgen(res, token.level, content_stub)

    # we cannot use attach_to_covering_ctx; as the top of the context 
    # is content stub
    if parent_ctx:
        logger.debug(f"heading is being attached to {parent_ctx}")
        parent_ctx.ctxhandle.components.append(mditem_view_stub_)
        return None
    else:
        return mditem_view_stub_


def openCloseCtx(hcgen):
    def owrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            renderer_obj = args[0]
            token = args[1]

            mditem_name = func.__name__.replace("render_", "")
            # check if user given renderer exists for this mditem
            # choose between user provided hcgen vs default hcgen
            mditem_name = func.__name__.replace("render_", "")
            view_func_name = mditem_name + "_view_handler"

            if view_func_name in renderer_obj.mditem_viewer_handler_map:
                given_hcgen = renderer_obj.mditem_viewer_handler_map[view_func_name]
                mditem_view_stub = given_hcgen()
                mditem_ctxstack = renderer_obj.mditem_ctxstack
                parent_ctx = None
                if len(mditem_ctxstack) > 0:
                    parent_ctx = mditem_ctxstack[-1]
                
                append_covering_ctx(mditem_ctxstack,  mditem_name,  mditem_view_stub)
                res = func(*args,  **kwargs, stub=mditem_view_stub)
                pop_covering_ctx(mditem_ctxstack, mditem_name)
                #attach the item to top-most 

                if parent_ctx:
                    parent_ctx.ctxhandle.components.append(mditem_view_stub)
                    return None
                else:
                    return mditem_view_stub
                
            else:
                stub_ = hcgen(childs=[])
                mditem_ctxstack = renderer_obj.mditem_ctxstack
                parent_ctx = None
                if len(mditem_ctxstack) > 0:
                    parent_ctx = mditem_ctxstack[-1]
                
                append_covering_ctx(mditem_ctxstack,  mditem_name,  stub_)
                res = func(*args,  **kwargs, stub=stub_)
                pop_covering_ctx(mditem_ctxstack, mditem_name)

                #attach the item to top-most 

                if parent_ctx:
                    parent_ctx.ctxhandle.components.append(stub_)
                    return None
                else:
                    return stub_

        return wrapper
    return owrapper

def captureViewDirective(renderer_obj, token):
    """
    L6 headings are view directives; should be removed from rendering 
    """
    if token.level == 6:

        renderer_obj.parsing_in_meta_mode = True
        inner = [_ for _ in renderer_obj.render_inner(token) if _ is not None]
        # e.g. for input line as ###### list_view_handler:view_list
        # the collected value will be :  [{'rawText': 'list_view_handler:view_list'}]
        
        renderer_obj.parsing_in_meta_mode = False
        view_directive = inner[0].rawText
        handler_type, handler_funcname = view_directive.split(":")
        if handler_funcname != 'None':
            renderer_obj.mditem_viewer_handler_map[handler_type] = renderer_obj.user_mditem_viewer_map[handler_funcname]
        else:
            
            if handler_type in renderer_obj.user_mditem_viewer_map:
                renderer_obj.mditem_viewer_handler_map[handler_type]  = renderer_obj.user_mditem_viewer_map[handler_type]

            elif handler_type in renderer_obj.default_mditem_viewer_map:
                renderer_obj.mditem_viewer_handler_map[handler_type] = renderer_obj.default_mditem_viewer_map[handler_type]

            else:
                # this mditem doesn't have a default or user defined render
                del renderer_obj.mditem_viewer_handler_map[handler_type]
                pass
        return True
    else:
        return False


def process_heading(func):
    """
    parse the heading directive
    1. pluck out md_view_handlers directives
    2. openCtx
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        #logger.debug("Processing heading")
        renderer_obj = args[0]
        token = args[1]
        if not captureViewDirective(renderer_obj, token):
            # this is a real heading
            # process it like openCtx
            openHeadingCtx(func, renderer_obj, token, *args, **kwargs)
        pass
    return wrapper

def renderFromDictImpl(renderer_obj, mditem_name, hcgen, token ):
    renderer_obj.parsing_in_meta_mode = True
    content_dict = [renderer_obj.render(child) for child in  token.children]
    res = Dict({mditem_name: content_dict})
    mditem_view_stub_ = hcgen(res)
    
    renderer_obj.parsing_in_meta_mode = False
    return attach_to_covering_ctx(renderer_obj.mditem_ctxstack,  mditem_view_stub_)
    
def renderFromDict(func):
    """
    takes a misltetoe orig render function but
    calls the default/user mditem viwer.
    Child is collected as dict object
    
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        renderer_obj = args[0]
        token = args[1]
        mditem_name = func.__name__.replace("render_", "")
        view_func_name = mditem_name + "_view_handler"
        hcgen = renderer_obj.mditem_viewer_handler_map[view_func_name]
        return renderFromDictImpl(renderer_obj, mditem_name, hcgen, token)

    return wrapper


def parse_as_dict_or_via_hcgen(func):
    """
    only two options:
    if parsing_in_meta_mode is on: then return as dict
    or
    call the default/user provided hcgen
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        renderer_obj = args[0]
        token = args[1]
        logger.debug(f"parsing {func}")
        if renderer_obj.parsing_in_meta_mode:
            logger.debug(f"parse as dict: {func}")
            res = func(*args, asdict=True)
            logger.debug(f"res = {res}")
            return res
        
        # all paragraphs are to rendered by default/user provided view renderer function
        mditem_name = func.__name__.replace("render_", "")
        view_func_name = mditem_name + "_view_handler"
        hcgen = renderer_obj.mditem_viewer_handler_map[view_func_name]
        return renderFromDictImpl(renderer_obj, mditem_name, hcgen, token)
    

    return wrapper

def renderHC(func):
    """
    for markdown items with openCtx and
    that which we know are not be returned as dict
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        renderer_obj = args[0]
        token = args[1]
        mditem_ctxstack = renderer_obj.mditem_ctxstack
        mditem_name = func.__name__.replace("render_", "")
        view_func_name = mditem_name + "_view_handler"
        collect_as_dict = True
        #logger.info("renderDictOrHC invoked")
        hcstub = func(*args, **kwargs)
        return hcstub

    return wrapper



