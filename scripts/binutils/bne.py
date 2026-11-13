#========================================================================
# bne.py
#========================================================================
# Operand syntax and machine encoding for bne

from .helpers import extract_field
from .helpers import Inst, Word, format_register, parse_register, parse_target

MASK  = 0x707f
MATCH = 0x1063

#------------------------------------------------------------------------
# parse
#------------------------------------------------------------------------

def parse( operands ):

  if len(operands) != 3:
    raise ValueError( "bne requires rs1, rs2, target" )

  reg1, reg2, token = operands
  rs1 = parse_register( reg1 )
  rs2 = parse_register( reg2 )

  target = parse_target( token )

  return Inst( "bne", (rs1, rs2, target) )

#------------------------------------------------------------------------
# format_asm
#------------------------------------------------------------------------

def format_asm( inst ):

  rs1, rs2, target = inst.operands
  return f"bne {format_register(rs1)}, {format_register(rs2)}, {target}"

#------------------------------------------------------------------------
# encode
#------------------------------------------------------------------------

def encode( pc, inst ):

  rs1, rs2, target = inst.operands

  if isinstance( target, str ):
    raise ValueError( f"unresolved bne target: {target}" )

  offset = target - pc
  if target % 4:
    raise ValueError( f"unaligned bne target: {target}" )
  if not -(1 << 12) <= offset < (1 << 12):
    raise ValueError( f"bne target out of range at address {pc}: {target}" )

  # Pack the displacement bits in B-type order: 12, 10:5, 4:1, 11

  imm_12   = extract_field( offset, 12, 12 )
  imm_10_5 = extract_field( offset, 10, 5 )
  imm_4_1  = extract_field( offset, 4, 1 )
  imm_11   = extract_field( offset, 11, 11 )
  imm_fields = (imm_12 << 31) | (imm_10_5 << 25) | (imm_4_1 << 8) | (imm_11 << 7)

  return Word( pc, imm_fields | (rs2 << 20) | (rs1 << 15) | MATCH )

#------------------------------------------------------------------------
# decode
#------------------------------------------------------------------------

def decode( pc, value ):

  rs1      = extract_field( value, 19, 15 )
  rs2      = extract_field( value, 24, 20 )
  imm_12   = extract_field( value, 31, 31 )
  imm_10_5 = extract_field( value, 30, 25 )
  imm_4_1  = extract_field( value, 11, 8 )
  imm_11   = extract_field( value, 7, 7 )

  # Recover the signed displacement before adding it to the branch PC

  offset = (imm_11 << 11) + (imm_10_5 << 5) + (imm_4_1 << 1) - (imm_12 << 12)
  target = pc + offset
  if target % 4:
    raise ValueError( f"unaligned bne target at address {pc}: {target}" )

  return Inst( "bne", (rs1, rs2, target) )
