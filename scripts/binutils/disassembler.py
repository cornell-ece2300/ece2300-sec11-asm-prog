#========================================================================
# disassembler.py
#========================================================================
# Read a TinyRV1 memory image and format it as assembly source

import re

from .helpers import Word
from .inst import decode_inst, format_inst

#------------------------------------------------------------------------
# parse_image
#------------------------------------------------------------------------
# Each input line holds one word, starting at byte address zero

def parse_image( text ):

  lines = text.splitlines()
  if len(lines) != 128:
    raise ValueError( f"expected 128 words, found {len(lines)}" )

  image = []
  for index, line in enumerate( lines ):
    bits = line.strip()
    if not re.fullmatch( r"[01]{32}|[01]{8}(_[01]{8}){3}", bits ):
      raise ValueError( f"invalid binary word at address {index * 4}: {bits!r}" )
    image.append( int(bits, 2) )

  return image

#------------------------------------------------------------------------
# disassemble
#------------------------------------------------------------------------
# Print absolute branch targets and omit trailing data padding

def disassemble( image ):

  if len(image) != 128:
    raise ValueError( f"expected 128 words, found {len(image)}" )

  lines = [".text"]
  padding_addr = None

  for index, value in enumerate( image[:64] ):
    addr = index * 4
    if value == 0:
      if padding_addr is None:
        padding_addr = addr
      continue

    inst = decode_inst( Word(addr, value) )

    # Skipping an interior zero would move this instruction during
    # reassembly. The source grammar can only express trailing padding.

    if padding_addr is not None:
      raise ValueError( f"text padding at address {padding_addr} before instruction "
                        f"at address {addr} cannot be represented in assembly" )

    lines.append( "  " + format_inst(inst) )

  # Keep one word from the trailing run of zeros

  end = len(image)
  while end > 65 and image[end - 2] == image[end - 1] == 0:
    end -= 1

  lines.extend( ["", ".data"] )
  for value in image[64:end]:
    lines.append( f"  .word {value}" )

  return "\n".join(lines) + "\n"
