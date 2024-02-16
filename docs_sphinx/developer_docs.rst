
===============
Developer docs
===============

Stuff
=====

Data Structure
--------------

Managing covering context stack
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

data-structure

  mditem_ctxstack: []

  each item on stack is of type ctx
  
  .. code-block python
     
     class ctx(NamedTuple):
	  ctxtype: Any
	  ctxhandle: Any

operations

1. check_and_pop
   - check the ctxtype and if it already exists in the stack
     then pop all the way down till ctxtype element is popped out. 

    
2. append_covering_ctx(mditem_name, content_stub)

   - mditem_name: for heading is "heading" + token.level
   - content_stub: e.g. oj.PC.StackV
     
   attach ctx(mditem_name:ctxtype, content_stub:ctxhandle)
   
   TBD

   


   
