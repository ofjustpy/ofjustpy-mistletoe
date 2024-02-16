"""
Ofjustpy renderer for mistletoe.
"""
import logging
import os
if os:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    
import html
import re
from itertools import chain
from urllib.parse import quote
from addict import Dict
from mistletoe import block_token
from mistletoe import span_token
from mistletoe.block_token import HTMLBlock
from mistletoe.span_token import HTMLSpan
from mistletoe.base_renderer import BaseRenderer
from py_tailwind_utils import prose, W, max
from mistletoe.ofjustpy_renderer_helper import  (openCloseCtx,
                                                 renderFromDict,
                                                 renderHC,
                                                 process_heading,
                                                 parse_as_dict_or_via_hcgen
                                                 )

from inspect import getmembers, isfunction
import ofjustpy as oj
import traceback
import sys
from mistletoe import default_mditem_viewer_handler


class OfjustpyRenderer(BaseRenderer):
    """
    HTML renderer class.

    See mistletoe.base_renderer module for more info.
    """
    def __init__(self, *extras, **kwargs):
        """
        Args:
            extras (list): allows subclasses to add even more custom tokens.
        """
        self._suppress_ptag_stack = [False]
        super().__init__(*chain((HTMLBlock, HTMLSpan), extras))
        # html.entities.html5 includes entitydefs not ending with ';',
        # CommonMark seems to hate them, so...
        self._stdlib_charref = html._charref
        _charref = re.compile(r'&(#[0-9]+;'
                              r'|#[xX][0-9a-fA-F]+;'
                              r'|[^\t\n\f <&#;]{1,32};)')
        html._charref = _charref
        self.parsing_in_meta_mode = False
        # used to assign keys for oj element
        user_mditem_viewer_handler_module = kwargs.pop('mditem_viewer_handlers', None)

        default_mditem_viewer_handler_module = default_mditem_viewer_handler
        self.default_mditem_viewer_map = dict(getmembers(default_mditem_viewer_handler_module,
                                                         isfunction))

        user_mditem_viewer_map =  {}
        if user_mditem_viewer_handler_module:
            self.user_mditem_viewer_map = dict(getmembers(user_mditem_viewer_handler_module,
                                                          isfunction)
                                               )

        self.mditem_viewer_handler_map = {}
        for key in self.default_mditem_viewer_map.keys():
            if key in user_mditem_viewer_map:
                self.mditem_viewer_handler_map[key] = self.user_mditem_viewer_map[key]
            else:
                self.mditem_viewer_handler_map[key]  = self.default_mditem_viewer_map[key]
                
        self.mditem_ctxstack = []


    def __exit__(self, *args):
        super().__exit__(*args)
        html._charref = self._stdlib_charref

    def render_to_plain(self, token) -> str:
        if hasattr(token, 'children'):
            inner = [self.render_to_plain(child) for child in token.children]
            return ''.join(inner)
        return html.escape(token.content)

    def render_strong(self, token: span_token.Strong) -> str:
        assert False
        template = '<strong>{}</strong>'
        return template.format(self.render_inner(token))

    def render_emphasis(self, token: span_token.Emphasis) -> str:
        assert False
        template = '<em>{}</em>'
        return template.format(self.render_inner(token))

    def render_inline_code(self, token: span_token.InlineCode) -> str:
        assert False
        template = '<code>{}</code>'
        inner = html.escape(token.children[0].content)
        return template.format(inner)

    def render_strikethrough(self, token: span_token.Strikethrough) -> str:
        assert False
        template = '<del>{}</del>'
        return template.format(self.render_inner(token))

    @parse_as_dict_or_via_hcgen
    def render_image(self, token: span_token.Image, asdict=False) -> str:
        if asdict:
            return Dict({'img':
                         { 'src': token.src, 'title': token.title, 'alt': self.render_to_plain(token)}                })
        # a specified handler is used 
        raise ValueError

    @parse_as_dict_or_via_hcgen
    def render_link(self, token: span_token.Link, asdict=False) -> str:
        if asdict:
            # as dict we don't parse anything super compilicated 
            vv = [_ for _ in self.render_inner(token) if _ is not None]
            assert len(vv) == 1
            target = self.escape_url(token.target)
            title = html.escape(token.title)
            return Dict({'ahref': {'title' : title, 'target': target, 'desc': vv[0].rawText}})

        raise ValueError
        target = self.escape_url(token.target)
        title = html.escape(token.title)
        inner = self.render_inner(token)
        return oj.AC.A(key=f"A_{self.key_cursor}",
                     title=title,
                     href = target,
                     cgens=inner
                     )


    def render_auto_link(self, token: span_token.AutoLink) -> str:
        assert False
        template = '<a href="{target}">{inner}</a>'
        if token.mailto:
            target = 'mailto:{}'.format(token.target)
        else:
            target = self.escape_url(token.target)
        inner = self.render_inner(token)
        return template.format(target=target, inner=inner)

    def render_escape_sequence(self, token: span_token.EscapeSequence) -> str:
        return self.render_inner(token)


    @parse_as_dict_or_via_hcgen
    def render_raw_text(self, token: span_token.RawText, asdict=False, **kwargs) -> str:
        #asdict = kwargs.pop("asdict", False)
        if asdict:
            return Dict({'rawText': html.escape(token.content)})

        # no point in returning raw_text in Span
        # let default/user md handle it. 
        assert False 
        key = self.get_key("raw_text")
        return oj.PC.Span(text=html.escape(token.content))

    @staticmethod
    def render_html_span(token: span_token.HTMLSpan) -> str:
        return token.content


    # let default/user view handler render heading
    @process_heading
    def render_heading(self, token: block_token.Heading, content_stub=None, asdict=False) -> str:

        if asdict:
            # Grab the text next to heading
            self.parsing_in_meta_mode = True
            inner = [self.render(child) for child in token.children]
            
            #inner = [_ for _ in self.render_inner(token.children) if _ is not None]

            self.parsing_in_meta_mode = False

            return Dict({'heading':  inner})
        
        # try:
        #     heading_text = inner[0].rawText
        # except:
        #     raise ValueError("Cannot deduce heading text for  heading item..markdown content too fancy for this renderer")
        # key = self.get_key("heading")
        # return oj.Subsubsection_(key, heading_text, content_stub)
        
        # heading is rendered using default viewer
        assert False

    def render_quote(self, token: block_token.Quote) -> str:
        elements = ['<blockquote>']
        self._suppress_ptag_stack.append(False)
        elements.extend([self.render(child) for child in token.children])
        self._suppress_ptag_stack.pop()
        elements.append('</blockquote>')
        return '\n'.join(elements)

    @parse_as_dict_or_via_hcgen
    def render_paragraph(self, token: block_token.Paragraph, asdict=False) -> str:
        # all paragraphs are captured as dict;
        if asdict:
            inner = [self.render(child) for child in token.children]
            return Dict({'para':  inner})
        
        assert False
    
    def render_block_code(self, token: block_token.BlockCode) -> str:
        template = '<pre><code{attr}>{inner}</code></pre>'
        if token.language:
            attr = ' class="{}"'.format('language-{}'.format(html.escape(token.language)))
        else:
            attr = ''
        inner = html.escape(token.children[0].content)
        return template.format(attr=attr, inner=inner)

    @openCloseCtx(oj.PC.Ul)
    def render_list(self, token: block_token.List, stub=None) -> str: # 
        """
        """
        assert stub is not None
        inner = [_ for _ in self.render_inner(token) if _ is not None]
        return stub
        

    # we expect list item to be really simple: just some text 
    @renderFromDict
    def render_list_item(self, token: block_token.ListItem) -> str:
        #This is never called
        #The dict is collected and default/user render function is used
        assert False
        pass
    
    def render_table(self, token: block_token.Table) -> str:
        # This is actually gross and I wonder if there's a better way to do it.
        #
        # The primary difficulty seems to be passing down alignment options to
        # reach individual cells.
        template = '<table>\n{inner}</table>'
        if hasattr(token, 'header'):
            head_template = '<thead>\n{inner}</thead>\n'
            head_inner = self.render_table_row(token.header, is_header=True)
            head_rendered = head_template.format(inner=head_inner)
        else: head_rendered = ''
        body_template = '<tbody>\n{inner}</tbody>\n'
        body_inner = self.render_inner(token)
        body_rendered = body_template.format(inner=body_inner)
        return template.format(inner=head_rendered+body_rendered)

    def render_table_row(self, token: block_token.TableRow, is_header=False) -> str:
        template = '<tr>\n{inner}</tr>\n'
        inner = ''.join([self.render_table_cell(child, is_header)
                         for child in token.children])
        return template.format(inner=inner)

    def render_table_cell(self, token: block_token.TableCell, in_header=False) -> str:
        template = '<{tag}{attr}>{inner}</{tag}>\n'
        tag = 'th' if in_header else 'td'
        if token.align is None:
            align = 'left'
        elif token.align == 0:
            align = 'center'
        elif token.align == 1:
            align = 'right'
        attr = ' align="{}"'.format(align)
        inner = self.render_inner(token)
        return template.format(tag=tag, attr=attr, inner=inner)

    @staticmethod
    def render_thematic_break(token: block_token.ThematicBreak) -> str:
        return '<hr />'


    @parse_as_dict_or_via_hcgen
    def render_line_break(self, token: span_token.LineBreak, asdict = False) -> str:
        if asdict:
            return Dict({'br': True})
        raise ValueError
        return '\n' if token.soft else '<br />\n'

    @staticmethod
    def render_html_block(token: block_token.HTMLBlock) -> str:
        return token.content

    @openCloseCtx(oj.PC.Div)
    def render_document(self, token: block_token.Document, stub=None) -> str:

        assert stub is not None
        inner = [_ for _ in self.render_inner(token) if _ is not None]
        #print ("inner ", inner)
        #if inner:
        return stub
        # if there is no content then don't create any htmlcomponent 
        #return None

    @staticmethod
    def escape_html(raw: str) -> str:
        """
        This method is deprecated. Use `html.escape` instead.
        """
        return html.escape(raw)

    @staticmethod
    def escape_url(raw: str) -> str:
        """
        Escape urls to prevent code injection craziness. (Hopefully.)
        """
        return html.escape(quote(raw, safe='/#:()*?=%@+,&;'))
