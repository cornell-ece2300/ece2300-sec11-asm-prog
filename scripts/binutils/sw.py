#========================================================================
# sw.py
#========================================================================
# Operand syntax and machine encoding for sw

import re

from .helpers import extract_field
from .helpers import Inst, Word, format_register, parse_imm12, parse_register, signed_imm12

# Match opcode and funct3 while ignoring the operand fields

MASK  = 0x707f
MATCH = 0x2023

#------------------------------------------------------------------------
# parse
#------------------------------------------------------------------------

def parse( operands ):

  if len(operands) != 2:
    raise ValueError( "sw requires rs2, offset(base)" )

  rs2, addr = operands
  match = re.fullmatch( r"([^()\s]+)\s*\(\s*([^()\s]+)\s*\)", addr )
  if not match:
    raise ValueError( f"invalid sw address: {addr!r}" )

  imm, rs1 = match.groups()
  return Inst( "sw", (parse_register(rs2), parse_imm12(imm), parse_register(rs1)) )

#------------------------------------------------------------------------
# format_asm
#------------------------------------------------------------------------

def format_asm( inst ):

  rs2, imm, rs1 = inst.operands
  return f"sw {format_register(rs2)}, {imm}({format_register(rs1)})"

#------------------------------------------------------------------------
# encode
#------------------------------------------------------------------------

def encode( pc, inst ):

  rs2, imm, rs1 = inst.operands

  # Split the offset between bits 31:25 and 11:7 of the store instruction

  imm_11_5 = extract_field( imm, 11, 5 )
  imm_4_0  = extract_field( imm, 4, 0 )

  return Word( pc, (imm_11_5 << 25) | (rs2 << 20) | (rs1 << 15) | (imm_4_0 << 7) | MATCH )

#------------------------------------------------------------------------
# decode
#------------------------------------------------------------------------

def decode( value ):

  rs2 = extract_field( value, 24, 20 )
  rs1 = extract_field( value, 19, 15 )

  # Reassemble the 12-bit offset before formatting it as signed decimal

  imm_11_5 = extract_field( value, 31, 25 )
  imm_4_0  = extract_field( value, 11, 7 )
  imm = (imm_11_5 << 5) | imm_4_0

  return Inst( "sw", (rs2, signed_imm12(imm), rs1) )
