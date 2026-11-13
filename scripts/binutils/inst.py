#========================================================================
# inst.py
#========================================================================
# Parse, format, encode, and decode TinyRV1 instructions

from . import add, addi, bne, jal, jr, lw, mul, sw
from .helpers import Inst

INSTRUCTIONS = { "addi": addi, "add": add, "mul": mul, "lw": lw, "sw": sw, "jal": jal, "jr": jr, "bne": bne }

#------------------------------------------------------------------------
# parse_inst
#------------------------------------------------------------------------
# Read one instruction body and return its mnemonic and canonical
# operands

def parse_inst( text ):

  fields = text.split( None, 1 )
  if not fields:
    raise ValueError( "missing instruction" )

  operands = ()
  if len(fields) == 2:
    operands = tuple( token.strip() for token in fields[1].split(",") )

  mnemonic = fields[0]
  module = INSTRUCTIONS.get( mnemonic )
  if module is None:
    raise ValueError( f"unknown instruction: {mnemonic}" )

  return module.parse( operands )

#------------------------------------------------------------------------
# format_inst
#------------------------------------------------------------------------
# Write one instruction in canonical assembly syntax

def format_inst( inst ):

  module = INSTRUCTIONS.get( inst.mnemonic )
  if module is None:
    raise ValueError( f"unknown instruction: {inst.mnemonic}" )

  return module.format_asm( inst )

#------------------------------------------------------------------------
# resolve_inst
#------------------------------------------------------------------------

def resolve_inst( inst, symbols ):

  # Parsing leaves only label operands as strings

  if all( isinstance(operand, int) for operand in inst.operands ):
    return inst

  operands = []
  for operand in inst.operands:
    if isinstance( operand, str ):
      if operand not in symbols:
        raise ValueError( f"undefined label: {operand}" )
      operand = symbols[operand]
    operands.append( operand )

  return Inst( inst.mnemonic, tuple(operands) )

#------------------------------------------------------------------------
# _check_pc
#------------------------------------------------------------------------
# Require an aligned byte address in the 64-word text section

def _check_pc( pc ):

  if type(pc) is not int or not 0 <= pc < 0x100 or pc % 4:
    raise ValueError( f"invalid text address: {pc}" )

#------------------------------------------------------------------------
# encode_inst
#------------------------------------------------------------------------
# Validate the text address and select the instruction encoder

def encode_inst( pc, inst ):

  _check_pc( pc )

  module = INSTRUCTIONS.get( inst.mnemonic )
  if module is None:
    raise ValueError( f"unknown instruction: {inst.mnemonic}" )

  return module.encode( pc, inst )

#------------------------------------------------------------------------
# decode_inst
#------------------------------------------------------------------------
# Validate a text word and select its instruction decoder

def decode_inst( word ):

  _check_pc( word.addr )
  value = word.value
  if type(value) is not int or not 0 <= value <= 0xffffffff:
    raise ValueError( f"invalid word at address {word.addr}: {value}" )

  for module in INSTRUCTIONS.values():
    if value & module.MASK == module.MATCH:
      if module in (jal, bne):
        return module.decode( word.addr, value )
      return module.decode( value )

  raise ValueError( f"unknown encoding at address {word.addr}: {value}" )
