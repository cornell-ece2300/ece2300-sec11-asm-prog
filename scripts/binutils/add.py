#========================================================================
# add.py
#========================================================================
# Operand syntax and machine encoding for add

from .helpers import extract_field
from .helpers import Inst, Word, format_register, parse_register

# Match opcode, funct3, and funct7 while ignoring the operand fields

MASK  = 0xfe00707f
MATCH = 0x33

#------------------------------------------------------------------------
# parse
#------------------------------------------------------------------------

def parse( operands ):

  if len(operands) != 3:
    raise ValueError( "add requires rd, rs1, rs2" )

  rd, rs1, rs2 = operands
  return Inst( "add", (parse_register(rd), parse_register(rs1), parse_register(rs2)) )

#------------------------------------------------------------------------
# format_asm
#------------------------------------------------------------------------

def format_asm( inst ):

  rd, rs1, rs2 = inst.operands
  return f"add {format_register(rd)}, {format_register(rs1)}, {format_register(rs2)}"

#------------------------------------------------------------------------
# encode
#------------------------------------------------------------------------

def encode( pc, inst ):

  rd, rs1, rs2 = inst.operands

  # ADD uses zero for both funct7 and funct3

  return Word( pc, (rs2 << 20) | (rs1 << 15) | (rd << 7) | 0x33 )

#------------------------------------------------------------------------
# decode
#------------------------------------------------------------------------

def decode( value ):

  rd  = extract_field( value, 11, 7 )
  rs1 = extract_field( value, 19, 15 )
  rs2 = extract_field( value, 24, 20 )

  return Inst( "add", (rd, rs1, rs2) )

