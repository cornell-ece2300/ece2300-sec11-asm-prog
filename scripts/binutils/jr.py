#========================================================================
# jr.py
#========================================================================
# Operand syntax and machine encoding for jr

from .helpers import Inst, Word, extract_field, format_register, parse_register

# Only rs1 in bits 19:15 varies in a JR instruction

MASK  = 0xfff07fff
MATCH = 0x67

#------------------------------------------------------------------------
# parse
#------------------------------------------------------------------------

def parse( operands ):

  if len(operands) != 1:
    raise ValueError( "jr requires rs1" )

  rs1 = parse_register( operands[0] )
  return Inst( "jr", (rs1,) )

#------------------------------------------------------------------------
# format_asm
#------------------------------------------------------------------------

def format_asm( inst ):

  rs1, = inst.operands
  return f"jr {format_register(rs1)}"

#------------------------------------------------------------------------
# encode
#------------------------------------------------------------------------

def encode( pc, inst ):

  rs1, = inst.operands
  return Word( pc, (rs1 << 15) | MATCH )

#------------------------------------------------------------------------
# decode
#------------------------------------------------------------------------

def decode( value ):

  rs1 = extract_field( value, 19, 15 )
  return Inst( "jr", (rs1,) )
