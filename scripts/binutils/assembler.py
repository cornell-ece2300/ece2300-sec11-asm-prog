#========================================================================
# assembler.py
#========================================================================
# Assemble TinyRV1 source into a 128-word memory image

import re
from collections import namedtuple

from .helpers import Word, parse_literal
from .inst import parse_inst, resolve_inst, encode_inst

# Each statement carries its original line number and section. The kind
# tells the next pass how to read the value: a label name, a .word
# operand, or an Inst.

Statement = namedtuple( "Statement", "lineno section addr kind value" )

#------------------------------------------------------------------------
# parse_source
#------------------------------------------------------------------------

def parse_source( text, filename="<input>" ):

  # An opening .text is optional. The first label or instruction also
  # opens .text. Track opened sections so each can appear only once.

  statements = []
  symbols = {}
  addr = 0
  section = ".text"
  seen = set()

  # Number the original lines before skipping comments and blank lines so
  # later passes can report errors using the same line numbers students
  # see.

  for lineno, line in enumerate( text.splitlines(), 1 ):
    stmt = line.partition("#")[0].strip()
    if not stmt:
      continue

    try:

      # A label takes up no space. Record it before the instruction so
      # both get the same byte address when addresses are assigned.

      if ":" in stmt:
        label, _, stmt = stmt.partition(":")
        label = label.strip()
        if section == ".data":
          raise ValueError( f"label in .data: {label!r}" )

        if not re.fullmatch( r"[A-Za-z_][A-Za-z0-9_]*", label ):
          raise ValueError( f"invalid label: {label!r}" )

        if label in symbols:
          raise ValueError( f"duplicate label: {label}" )

        symbols[label] = addr
        seen.add( section )
        statements.append( Statement(lineno, section, addr, "label", label) )
        stmt = stmt.strip()
        if not stmt:
          continue

      fields = stmt.split( None, 1 )
      name = fields[0]

      # A selector changes the section attached to subsequent statements.
      # Keep previously used sections in seen so a second region is
      # rejected.

      if name in (".text", ".data"):
        if len(fields) != 1:
          raise ValueError( f"{name} takes no operands" )
        if section == ".data" and name == ".text":
          raise ValueError( ".text must come before .data" )
        if name in seen:
          raise ValueError( f"repeated {name} region" )

        if name == ".data":
          addr = 256

        section = name
        seen.add( section )
        continue

      seen.add( section )

      # Keep the numeric value for the emitter

      if name == ".word":
        if section != ".data":
          raise ValueError( ".word requires the .data section" )
        if len(fields) != 2:
          raise ValueError( ".word requires an integer literal" )
        if addr >= 512:
          raise ValueError( ".data exceeds 64 words" )
        value = parse_literal( fields[1] )
        statements.append( Statement(lineno, section, addr, "word", value) )

      elif name.startswith("."):
        raise ValueError( f"unknown directive: {name}" )

      else:
        # Let the instruction parser handle the mnemonic and operand
        # syntax

        if section == ".data":
          raise ValueError( "instructions belong in .text before .data" )

        if addr >= 256:
          raise ValueError( ".text exceeds 64 words" )

        inst = parse_inst( stmt )
        statements.append( Statement(lineno, section, addr, "inst", inst) )

      addr += 4

    except ValueError as error:
      message = f"{filename}:{lineno}: error: {error}\n  {line.strip()}"
      raise ValueError( message ) from None

  return statements, symbols

#------------------------------------------------------------------------
# resolve_statements
#------------------------------------------------------------------------
# Resolve instructions and collect data words in source order

def resolve_statements( statements, symbols, text=None, filename="<input>" ):

  entries = []

  for stmt in statements:
    if stmt.kind == "label":
      continue

    try:

      # Keep absolute targets and PCs until the instruction is encoded

      if stmt.kind == "inst":
        inst = resolve_inst( stmt.value, symbols )
        entries.append( (stmt.addr, inst) )

      elif stmt.kind == "word":
        value = stmt.value
        if not -(1 << 31) <= value < (1 << 32):
          raise ValueError( f".word value out of 32-bit range: {value}" )

        # Store negative literals as unsigned two's-complement words

        entries.append( Word(stmt.addr, value & 0xffffffff) )

      else:
        raise ValueError( f"unknown statement kind: {stmt.kind}" )

    except ValueError as error:
      message = f"{filename}:{stmt.lineno}: error: {error}"
      if text is not None:
        line = text.splitlines()[stmt.lineno - 1]
        message += f"\n  {line.strip()}"
      raise ValueError( message ) from None

  return entries

#------------------------------------------------------------------------
# emit_image
#------------------------------------------------------------------------
# Encode resolved instructions and place each word at its byte address

def emit_image( entries, source_lines=None, filename="<input>" ):

  image = [0] * 128

  for entry in entries:
    if isinstance( entry, Word ):
      word = entry

    else:
      pc, inst = entry
      try:
        word = encode_inst( pc, inst )
      except ValueError as error:
        if source_lines is None:
          raise
        lineno, line = source_lines[pc]
        message = f"{filename}:{lineno}: error: {error}\n  {line.strip()}"
        raise ValueError( message ) from None

    # Addresses count bytes while the image holds four-byte words

    image[word.addr // 4] = word.value

  return image

#------------------------------------------------------------------------
# assemble
#------------------------------------------------------------------------
# Run the three passes and return the complete memory image

def assemble( text, filename="<input>" ):

  statements, symbols = parse_source( text, filename )
  entries = resolve_statements( statements, symbols, text, filename )

  # Keep the original instruction lines for errors found during encoding

  lines = text.splitlines()
  source_lines = { stmt.addr: (stmt.lineno, lines[stmt.lineno - 1])
                   for stmt in statements if stmt.kind == "inst" }

  return emit_image( entries, source_lines, filename )
