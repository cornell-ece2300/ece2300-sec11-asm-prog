#========================================================================
# listing.py
#========================================================================
# Format an assembled memory image for the console

from .helpers import Word
from .inst import decode_inst, format_inst

#------------------------------------------------------------------------
# format_machine_word
#------------------------------------------------------------------------

def format_machine_word( value ):

  bits = f"{value:032b}"
  return "_".join( bits[i:i+8] for i in range(0, 32, 8) )

#------------------------------------------------------------------------
# format_listing
#------------------------------------------------------------------------

def format_listing( image ):

  divider = "-" * 68
  lines = [ "addr  addr", "(dec) (hex) assembly inst        machine inst", divider ]

  for index, value in enumerate( image[:64] ):
    if value == 0:
      continue

    addr = index * 4
    asm = format_inst( decode_inst(Word(addr, value)) )
    machine = format_machine_word( value )
    lines.append( f"{addr:5} {addr:#05x} {asm:20} {machine}" )

  lines.extend( ["", "addr  addr", "(dec) (hex) data", divider] )
  index = 64
  while index < len(image):
    addr = index * 4
    value = image[index]
    lines.append( f"{addr:5} {addr:#05x} {value:#010x}" )
    index += 1

    # Represent the remaining words in this zero run with one ellipsis

    if value == 0 and index < len(image) and image[index] == 0:
      lines.append( "  ..." )
      while index < len(image) and image[index] == 0:
        index += 1

  return "\n".join( lines )
