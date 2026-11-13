#========================================================================
# lw.py
#========================================================================
# Operand syntax and machine encoding for lw

import re

from .helpers import extract_field
from .helpers import Inst, Word, format_register, parse_imm12, parse_register, signed_imm12

# Match opcode and funct3 while ignoring the operand fields

MASK  = 0x707f
MATCH = 0x2003

#------------------------------------------------------------------------
# parse
#------------------------------------------------------------------------

def parse( operands ):

  if len(operands) != 2:
    raise ValueError( "lw requires rd, offset(base)" )

  rd, addr = operands
  match = re.fullmatch( r"([^()\s]+)\s*\(\s*([^()\s]+)\s*\)", addr )
  if not match:
    raise ValueError( f"invalid lw address: {addr!r}" )

  imm, rs1 = match.groups()
  return Inst( "lw", (parse_register(rd), parse_imm12(imm), parse_register(rs1)) )

#------------------------------------------------------------------------
# format_asm
#------------------------------------------------------------------------

def format_asm( inst ):

  rd, imm, rs1 = inst.operands
  return f"lw {format_register(rd)}, {imm}({format_register(rs1)})"

#------------------------------------------------------------------------
# encode
#------------------------------------------------------------------------

def encode( pc, inst ):

  rd, imm, rs1 = inst.operands

  # I-type layout: imm[31:20], rs1[19:15], funct3[14:12], rd[11:7],
  # opcode[6:0]. For lw, funct3 is 2 and the opcode is 0x03.

  return Word( pc, ((imm & 0xfff) << 20) | (rs1 << 15) | (rd << 7) | MATCH )

#------------------------------------------------------------------------
# decode
#------------------------------------------------------------------------

def decode( value ):

  rd  = extract_field( value, 11, 7 )
  rs1 = extract_field( value, 19, 15 )
  imm = extract_field( value, 31, 20 )

  return Inst( "lw", (rd, signed_imm12(imm), rs1) )

