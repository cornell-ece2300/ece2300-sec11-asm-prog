#========================================================================
# addi.py
#========================================================================
# Operand syntax and machine encoding for addi

from .helpers import extract_field
from .helpers import Inst, Word, format_register, parse_imm12, parse_register, signed_imm12

# Match opcode and funct3 while ignoring the operand fields

MASK  = 0x707f
MATCH = 0x13

#------------------------------------------------------------------------
# parse
#------------------------------------------------------------------------

def parse( operands ):

  if len(operands) != 3:
    raise ValueError( "addi requires rd, rs1, imm" )

  rd, rs1, imm = operands
  return Inst( "addi", (parse_register(rd), parse_register(rs1), parse_imm12(imm)) )

#------------------------------------------------------------------------
# format_asm
#------------------------------------------------------------------------

def format_asm( inst ):

  rd, rs1, imm = inst.operands
  return f"addi {format_register(rd)}, {format_register(rs1)}, {imm}"

#------------------------------------------------------------------------
# encode
#------------------------------------------------------------------------

def encode( pc, inst ):

  rd, rs1, imm = inst.operands

  # I-type layout: imm[31:20], rs1[19:15], funct3[14:12], rd[11:7],
  # opcode[6:0]. For addi, funct3 is zero and the opcode is 0x13.

  return Word( pc, ((imm & 0xfff) << 20) | (rs1 << 15) | (rd << 7) | 0x13 )

#------------------------------------------------------------------------
# decode
#------------------------------------------------------------------------

def decode( value ):

  rd  = extract_field( value, 11, 7 )
  rs1 = extract_field( value, 19, 15 )
  imm = extract_field( value, 31, 20 )

  return Inst( "addi", (rd, rs1, signed_imm12(imm)) )

