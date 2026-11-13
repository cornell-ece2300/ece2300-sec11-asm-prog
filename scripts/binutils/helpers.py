#========================================================================
# helpers.py
#========================================================================
# Register and integer literal helpers for the TinyRV1 tools

import re
from collections import namedtuple

#------------------------------------------------------------------------
# Assembly value types
#------------------------------------------------------------------------

Inst = namedtuple( "Inst", "mnemonic operands" )
Word = namedtuple( "Word", "addr value" )
Bits = namedtuple( "Bits", "width value" )

#------------------------------------------------------------------------
# parse_register
#------------------------------------------------------------------------
# Parse an x-register token and return its index from 0 through 31

def parse_register( token ):

  if not re.fullmatch( r"x[0-9]+", token ):
    raise ValueError( f"invalid register {token!r}" )

  index = int( token[1:] )
  if index > 31:
    raise ValueError( f"register out of range: {token!r}" )

  return index

#------------------------------------------------------------------------
# format_register
#------------------------------------------------------------------------
# Format a valid register index as x0 through x31 without leading zeros

def format_register( index ):

  if type(index) is not int or not 0 <= index < 32:
    raise ValueError( f"invalid register index {index!r}" )

  return f"x{index}"

#------------------------------------------------------------------------
# _check_width
#------------------------------------------------------------------------
# Raise ValueError unless the bit width is a positive integer

def _check_width( width ):

  if type(width) is not int or width < 1:
    raise ValueError( f"invalid bit width {width!r}" )

#------------------------------------------------------------------------
# parse_bits
#------------------------------------------------------------------------
# Read signed decimal or unsigned hexadecimal. Store a negative value
# in two's complement and reject values outside the given width.

def parse_bits( token, width ):

  _check_width( width )

  if re.fullmatch( r"[+-]?[0-9]+", token ):
    value = int( token, 10 )
  elif re.fullmatch( r"0[xX][0-9a-fA-F]+", token ):
    value = int( token, 16 )
  else:
    raise ValueError( f"invalid integer literal {token!r}" )

  limit = 1 << width
  if not -(limit // 2) <= value < limit:
    raise ValueError( f"{token!r} does not fit in {width} bits" )

  return Bits( width, value % limit )

#------------------------------------------------------------------------
# format_bits
#------------------------------------------------------------------------
# Check that the unsigned value fits its width and write it in decimal

def format_bits( bits ):

  _check_width( bits.width )
  if type(bits.value) is not int or not 0 <= bits.value < (1 << bits.width):
    raise ValueError( f"invalid unsigned {bits.width}-bit value {bits.value!r}" )

  return str( bits.value )

#------------------------------------------------------------------------
# extract_field
#------------------------------------------------------------------------
# Return the unsigned field value[hi:lo], including both endpoints

def extract_field( value, hi, lo ):

  if lo < 0 or hi < lo:
    raise ValueError( f"invalid bit range [{hi}:{lo}]" )

  width = hi - lo + 1
  mask = (1 << width) - 1

  return (value >> lo) & mask

#------------------------------------------------------------------------
# signed_imm12
#------------------------------------------------------------------------

def signed_imm12( value ):

  if value & 0x800:
    return value - 0x1000

  return value

#------------------------------------------------------------------------
# parse_imm12
#------------------------------------------------------------------------

def parse_imm12( token ):

  bits = parse_bits( token, 12 )

  # Hex supplies the raw bits while decimal supplies the signed value

  if not token.lower().startswith("0x") and int(token) > 2047:
    raise ValueError( f"signed immediate out of range: {token}" )

  return signed_imm12( bits.value )

#------------------------------------------------------------------------
# parse_literal
#------------------------------------------------------------------------
# Read a signed decimal or unsigned hex integer

def parse_literal( token ):

  if re.fullmatch( r"[+-]?[0-9]+", token ):
    return int( token, 10 )
  if re.fullmatch( r"0[xX][0-9a-fA-F]+", token ):
    return int( token, 16 )
  raise ValueError( f"invalid integer literal: {token!r}" )

#------------------------------------------------------------------------
# parse_target
#------------------------------------------------------------------------
# Read an absolute byte address or keep a label for resolution

def parse_target( token ):

  if re.fullmatch( r"[A-Za-z_][A-Za-z0-9_]*", token ):
    return token

  return parse_literal( token )
