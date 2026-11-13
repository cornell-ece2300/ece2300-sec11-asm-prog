#========================================================================
# jal.py
#========================================================================
# Operand syntax and machine encoding for jal

from .helpers import extract_field
from .helpers import Inst, Word, format_register, parse_register, parse_target

MASK  = 0x7f
MATCH = 0x6f

#------------------------------------------------------------------------
# parse
#------------------------------------------------------------------------

def parse( operands ):

  if len(operands) != 2:
    raise ValueError( "jal requires rd, target" )

  reg, token = operands
  rd = parse_register( reg )

  target = parse_target( token )

  return Inst( "jal", (rd, target) )

#------------------------------------------------------------------------
# format_asm
#------------------------------------------------------------------------

def format_asm( inst ):

  rd, target = inst.operands
  return f"jal {format_register(rd)}, {target}"

#------------------------------------------------------------------------
# encode
#------------------------------------------------------------------------

def encode( pc, inst ):

  rd, target = inst.operands

  if isinstance( target, str ):
    raise ValueError( f"unresolved jal target: {target}" )

  offset = target - pc
  if target % 4:
    raise ValueError( f"unaligned jal target: {target}" )
  if not -(1 << 20) <= offset < (1 << 20):
    raise ValueError( f"jal target out of range at address {pc}: {target}" )

  # Pack the displacement bits in J-type order: 20, 10:1, 11, 19:12

  imm_20    = extract_field( offset, 20, 20 )
  imm_10_1  = extract_field( offset, 10, 1 )
  imm_11    = extract_field( offset, 11, 11 )
  imm_19_12 = extract_field( offset, 19, 12 )
  imm_fields = (imm_20 << 31) | (imm_10_1 << 21) | (imm_11 << 20) | (imm_19_12 << 12)

  return Word( pc, imm_fields | (rd << 7) | MATCH )

#------------------------------------------------------------------------
# decode
#------------------------------------------------------------------------

def decode( pc, value ):

  rd        = extract_field( value, 11, 7 )
  imm_20    = extract_field( value, 31, 31 )
  imm_10_1  = extract_field( value, 30, 21 )
  imm_11    = extract_field( value, 20, 20 )
  imm_19_12 = extract_field( value, 19, 12 )

  # The sign bit contributes -2**20 to the signed displacement

  offset = (imm_19_12 << 12) + (imm_11 << 11) + (imm_10_1 << 1) - (imm_20 << 20)
  target = pc + offset
  if target % 4:
    raise ValueError( f"unaligned jal target at address {pc}: {target}" )

  return Inst( "jal", (rd, target) )
