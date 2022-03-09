#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This is file `coder-tool.x.py',
# generated with the docstrip utility.
#
# The original source files were:
#
# coder.dtx  (with options: `py')
# 
# coder --- code inlined in a LuaLaTeX document.
# version: v2.6a
# date: 2020-11-23
# url: https:github.com/jlaurens/coder
# E-mail: jerome.laurens@u-bourgogne.fr
# Released under the LaTeX Project Public License v1.3c or later
# See http://www.latex-project.org/lppl.txt
# 

#! /usr/bin/env python3
# -*- coding: utf-8 -*-
__version__ = '0.10'
__YEAR__  = '2022'
__docformat__ = 'restructuredtext'

from posixpath import split
import sys
import argparse
import re
from pathlib import Path
import hashlib
import json
from pygments import highlight as hilight
from pygments.formatters.latex import LatexEmbeddedLexer, LatexFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound
from pygments.util import guess_decode
class Options(object):
  @staticmethod
  def ensure_bool(x):
    if x == True or x == False: return x
    x = x[0:1]
    return x == 'T' or x == 't'
  def __new__(cls, d={}, *args, **kvargs):
    __cls__ = d.get('__cls__', 'arguments')
    if __cls__ == 'PygOpts':
      return super(Controller.Options, cls)['__new__'](
        Controller.PygOpts, *args, **kvargs
      )
    elif __cls__ == 'FVOpts':
      return super(Controller.Options, cls)['__new__'](
        Controller.FVOpts, *args, **kvargs
      )
    elif __cls__ == 'TeXOpts':
      return super(Controller.Options, cls)['__new__'](
        Controller.TeXOpts, *args, **kvargs
      )
    else:
      return super(Controller.Options, cls)['__new__'](
        Controller.Arguments, *args, **kvargs
      )
  def __init__(self, d={}):
    for k, v in d.items():
      if type(v) == str:
        if v.lower() == 'true':
          setattr(self, k, True)
          continue
        elif v.lower() == 'false':
          setattr(self, k, False)
          continue
      setattr(self, k, v)
  def __repr__(self):
    return f"{object['__repr__'](self)}: {self['__dict__']}"
class TeXOpts(Options):
  tags = ''
  inline = True
  already_style = False
  sty_template='<placeholder:style_defs>'
  code_template ='<placeholder:hilighted>'
  single_line_template='<placeholder:number><placeholder:line>'
  first_line_template='<placeholder:number><placeholder:line>'
  second_line_template='<placeholder:number><placeholder:line>'
  white_line_template='<placeholder:number><placeholder:line>'
  black_line_template='<placeholder:number><placeholder:line>'
  block_template='<placeholder:count><placeholder:hilighted>'
  def __init__(self, *args, **kvargs):
    super().__init__(*args, **kvargs)
    self.inline = self.ensure_bool(self.inline)
class PygOpts(Options):
  style = 'default'
  nobackground = False
  linenos = False
  linenostart = 1
  linenostep = 1
  commandprefix = 'Py'
  texcomments = False
  mathescape =  False
  escapeinside = ""
  envname = 'Verbatim'
  lang = 'tex'
  def __init__(self, *args, **kvargs):
    super().__init__(*args, **kvargs)
    self.linenos = Controller.ensure_bool(self.linenos)
    self.linenostart = abs(int(self.linenostart))
    self.linenostep  = abs(int(self.linenostep))
    self.texcomments = Controller.ensure_bool(self.texcomments)
    self.mathescape  = Controller.ensure_bool(self.mathescape)
class FVOpts(Options):
  gobble = 0
  tabsize = 4
  linenosep = '0pt'
  commentchar = ''
  frame = 'none'
  label = ''
  labelposition = 'none'
  numbers = 'left'
  numbersep = r'\hspace{1ex}'
  firstnumber = 'auto'
  stepnumber = 1
  numberblanklines = True
  firstline = ''
  lastline = ''
  baselinestretch = 'auto'
  resetmargins = True
  xleftmargin = '0pt'
  xrightmargin = '0pt'
  hfuzz = '2pt'
  samepage = False
  def __init__(self, *args, **kvargs):
    super().__init__(*args, **kvargs)
    self.gobble  = abs(int(self.gobble))
    self.tabsize  = abs(int(self.tabsize))
    if self.firstnumber != 'auto':
      self.firstnumber = abs(int(self.firstnumber))
    self.stepnumber = abs(int(self.stepnumber))
    self.linenostep  = abs(int(self.linenostep))
    self.numberblanklines = Controller.ensure_bool(self.numberblanklines)
    self.resetmargins  = Controller.ensure_bool(self.resetmargins)
    self.samepage  = Controller.ensure_bool(self.samepage)
class Arguments(Options):
  cache = False
  debug = False
  code = ""
  json = ""
  directory = "."
  texopts = TeXOpts()
  pygopts = PygOpts()
  fv_opts = FVOpts()
  directory = ""
class Controller:
  _json_p = None
  @property
  def json_p(self):
    p = self._json_p
    if p:
      return p
    else:
      p = self.arguments.json
      if p:
        p = Path(p).resolve()
    self._json_p = p
    return p
  _pygd_p = None
  @property
  def pygd_p(self):
    p = self._pygd_p
    if p:
      return p
    p = self.arguments.directory
    if p:
      p = Path(p)
    else:
      p = self.json_p
      if p:
        p = p.parent / p.stem
      else:
        p = Path('SHARED')
    if p:
      p = p.resolve().with_suffix(".pygd")
      p.mkdir(exist_ok=True)
    self._pygd_p = p
    return p
  @property
  def pyg_sty_p(self):
    return (self.pygd_p / self.pygopts.style).with_suffix(".pyg.sty")
  @property
  def parser(self):
    parser = argparse.ArgumentParser(
      prog=sys.argv[0],
      description='''
Writes to the output file a set of LaTeX macros describing
the syntax hilighting of the input file as given by pygments.
'''
    )
    parser.add_argument(
      "-v", "--version",
      help="Print the version and exit",
      action='version',
      version=f'coder-tool version {__version__},'
      ' (c) {__YEAR__} by Jérôme LAURENS.'
    )
    parser.add_argument(
      "--debug",
      default=None,
      help="display informations useful for debugging"
    )
    parser.add_argument(
      "json",
      metavar="json data file",
      help="""
file name with extension, contains processing information
"""
    )
    return parser

  @staticmethod
  def lua_command(cmd):
    print(f'<<<<<?LUA:{cmd}>>>>>')
  @staticmethod
  def lua_command_now(cmd):
    print(f'<<<<<!LUA:{cmd}>>>>>')
  def __init__(self, argv = sys.argv):
    argv = argv[1:] if re.match(".*coder\-tool\.py$", argv[0]) else argv
    ns = self.parser.parse_args(
      argv if len(argv) else ['-h']
    )
    with open(ns.json, 'r') as f:
      self.arguments = json.load(
        f,
        object_hook=Controller.Object
      )
    texopts = self.texopts = self.arguments.texopts
    pygopts = self.pygopts = self.arguments.pygopts
    fv_opts = self.fv_opts = self.arguments.fv_opts
    formatter = self.formatter = LatexFormatter(
      style=pygopts.style,
      nobackground = pygopts.nobackground,
      commandprefix = pygopts.commandprefix,
      texcomments = pygopts.texcomments,
      mathescape = pygopts.mathescape,
      escapeinside = pygopts.escapeinside,
      envname = u'CDR@Pyg@Verbatim',
    )

    try:
      lexer = self.lexer = get_lexer_by_name(self.arguments.lang)
    except ClassNotFound as err:
      sys.stderr.write('Error: ')
      sys.stderr.write(str(err))

    escapeinside = pygopts.escapeinside
    # When using the LaTeX formatter and the option `escapeinside` is
    # specified, we need a special lexer which collects escaped text
    # before running the chosen language lexer.
    if len(escapeinside) == 2:
      left  = escapeinside[0]
      right = escapeinside[1]
      lexer = self.lexer = LatexEmbeddedLexer(left, right, lexer)

    gobble = fv_opts.gobble
    if gobble:
      lexer.add_filter('gobble', n=gobble)
    tabsize = fv_opts.tabsize
    if tabsize:
      lexer.tabsize = tabsize
    lexer.encoding = ''

  def get_pyg_tex_p(self, digest):
    return (self.pygd_p / digest).with_suffix(".pyg.tex")
  def create_style(self):
    pyg_sty_p = self.pyg_sty_p
    if self.arguments.cache and pyg_sty_p.exists():
      print("Already available:", pyg_sty_p)
      return
    texopts = self.texopts
    if texopts.already_style:
      return
    formatter = self.formatter
    style_defs = formatter.get_style_defs() \
      .replace(r'\makeatletter', '') \
      .replace(r'\makeatother', '') \
      .replace('\n', '%\n')
    sty = self.texopts.sty_template.replace(
      '<placeholder:style_defs>',
      style_defs,
    )
    with pyg_sty_p.open(mode='w',encoding='utf-8') as f:
      f.write(sty)
  def pygmentize(self, code):
    code = hilight(code, self.lexer, self.formatter)
    m = re.match(
      r'\begin{CDR@Pyg@Verbatim}.*?\n(.*?)\n\end{CDR@Pyg@Verbatim}\s*\Z',
      code,
      flags=re.S
    )
    assert(m)
    hilighted = m.group(1)
    texopts = self.texopts
    if texopts.inline:
      return texopts.code_template.replace('<placeholder:hilighted>',hilighted)
    fv_opts = self.fv_opts
    lines = hilighted.split('\n')
    number = firstnumber = fv_opts.firstnumber
    stepnumber = fv_opts.stepnumber
    no = ''
    numbering = fv_opts.numbers != 'none'
    ans_code = []
    def more(template):
      ans_code.append(template.replace(
          '<placeholder:number>', f'{number}',
        ).replace(
          '<placeholder:line>', line,
      ))
      number += 1

    if len(lines) == 1:
      line = lines.pop(0)
      more(texopts.single_line_template)
    elif len(lines):
      line = lines.pop(0)
      more(texopts.first_line_template)
      line = lines.pop(0)
      more(texopts.second_line_template)
      if stepnumber < 2:
        def template():
          return texopts.black_line_template
      elif stepnumber % 5 == 0:
        def template():
          return texopts.black_line_template if number %\
            linenostep == 0 else texopts.white_line_template
      else:
        def template():
          return texopts.black_line_template if (number - firstnumber) %\
            linenostep == 0 else texopts.white_line_template

      for line in lines:
        more(template())

      hilighted = '\n'.join(ans_code)
      return texopts.block_template.replace(
        '<placeholder:count>', f'{counter-firstnumber}'
      ).replace(
        '<placeholder:hilighted>', hilighted
      )
#%
#%    ans_code.append(fr'''%
#%\begin{{CDR@Block/engine/{pygopts.style}}}
#%\CDRBlock@linenos@used:n {{{','.join(numbers)}}}%
#%{m.group(1)}{'\n'.join(lines)}{m.group(3)}%
#%\end{{CDR@Block/engine/{pygopts.style}}}
#%''' )
#%      ans_code = "".join(ans_code)
#%    return texopts.block_template.replace('<placeholder:hilighted>',hilighted)
  def create_pygmented(self):
    arguments = self.arguments
    code = arguments.code
    if not code:
      return False
    inline = self.texopts.inline
    h = hashlib.md5(f'{str(code)}:{inline}'.encode('utf-8'))
    pyg_tex_p = self.get_pyg_tex_p(h.hexdigest())
    if arguments.cache and pyg_tex_p.exists():
      print("Already available:", pyg_tex_p)
      return True
    code = self.pygmentize(code)
    with pyg_tex_p.open(mode='w',encoding='utf-8') as f:
      f.write(code)
    self.lua_command_now( f'self:input({pyg_tex_p})' )
# \CDR_remove:n {{colored:}}%
# \input {{ \tl_to_str:n {{}} }}%
# \CDR:n {{colored:}}%
    pyg_sty_p = self.pyg_sty_p
    if pyg_sty_p.parent.stem != 'SHARED':
      self.lua_command_now( fr'''
CDR:cache_record([=====[{pyg_sty_p.name}]=====],[=====[{pyg_tex_p.name}]=====])
''' )
    print("PREMATURE EXIT")
    exit(1)
if __name__ == '__main__':
  try:
    ctrl = Controller()
    x = ctrl.create_style() or ctrl.create_pygmented()
    print(f'{sys.argv[0]}: done')
    sys.exit(x)
  except KeyboardInterrupt:
    sys.exit(1)
