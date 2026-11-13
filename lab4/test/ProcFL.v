//========================================================================
// ProcFL
//========================================================================
// TinyRV1 functional-level model.

`ifndef PROC_FL_V
`define PROC_FL_V

`include "lab4/tinyrv1.v"

module ProcFL
(
  input  logic        clk,
  input  logic        rst,

  // Memory Bus External I/O

  input  logic [31:0] in0,
  input  logic [31:0] in1,
  input  logic [31:0] in2,
  input  logic [31:0] in3,

  output logic [31:0] out0,
  output logic [31:0] out1,
  output logic [31:0] out2,
  output logic [31:0] out3,

  // Trace interface

  output logic        trace_val,
  output logic [31:0] trace_pc,
  output logic [31:0] trace_inst,
  output logic        trace_wen,
  output logic  [4:0] trace_wreg,
  output logic [31:0] trace_wdata
);

  //----------------------------------------------------------------------
  // Register File
  //----------------------------------------------------------------------

  logic [31:0] R [32];

  task automatic rf_wr
  (
    input logic  [4:0] waddr,
    input logic [31:0] wdata
  );
    if ( waddr != 0 )
      R[waddr] = wdata;

    trace_wen   = 1'b1;
    trace_wreg  = waddr;
    trace_wdata = wdata;
  endtask

  //----------------------------------------------------------------------
  // Memory
  //----------------------------------------------------------------------

  logic [31:0] M [128];

  function [31:0] imem_rd
  (
    input logic [31:0] raddr
  );

    if ( raddr[1:0] != 2'b00 ) begin
      $display( `ECE2300_RED, "FAILED", `ECE2300_RESET,
                "\n\n Memory Access Error: Instruction mem address %0d is not word aligned!\n", raddr );
      $finish;
    end

    if ( raddr > 540 ) begin
      $display( `ECE2300_RED, "FAILED", `ECE2300_RESET,
                "\n\n Memory Access Error: Instruction mem address %0d is out of range!\n", raddr );
      $finish;
    end

    if ( raddr >= 256 ) begin
      $display( `ECE2300_RED, "FAILED", `ECE2300_RESET,
                "\n\n Memory Access Error: Cannot fetch instruction from address %0d!\n", raddr );
      $finish;
    end

    return M[ raddr[8:2] ];

  endfunction

  function void check_dmem_addr
  (
    input logic [31:0] raddr,
    input logic        write_en
  );

    if ( raddr[1:0] != 2'b00 ) begin
      $display( `ECE2300_RED, "FAILED", `ECE2300_RESET,
                "\n\n Memory Access Error: Data mem address %0d is not word aligned!\n", raddr );
      $finish;
    end

    if ( raddr > 540 ) begin
      $display( `ECE2300_RED, "FAILED", `ECE2300_RESET,
                "\n\n Memory Access Error: Data mem address %0d is out of range!\n", raddr );
      $finish;
    end

    if ( raddr < 256 ) begin
      $display( `ECE2300_RED, "FAILED", `ECE2300_RESET,
                "\n\n Memory Access Error: Cannot access address %0d using %s!\n", raddr, write_en ? "SW" : "LW" );
      $finish;
    end

  endfunction

  task dmem_wr
  (
    input logic [31:0] waddr,
    input logic [31:0] wdata
  );

    check_dmem_addr( waddr, 1'b1 );
    if ( waddr < 512 ) begin
      M[ waddr[8:2] ] = wdata;
    end
    else begin
      case ( waddr )
        528 : out0 = wdata;
        532 : out1 = wdata;
        536 : out2 = wdata;
        540 : out3 = wdata;
        default: ;
      endcase
    end
  endtask

  function [31:0] dmem_rd
  (
    input logic [31:0] raddr
  );

    check_dmem_addr( raddr, 1'b0 );
    if ( raddr < 512 ) begin
      return M[ raddr[8:2] ];
    end
    else begin
      case ( raddr )
        512 : return in0;
        516 : return in1;
        520 : return in2;
        524 : return in3;
        default : return 'x;
      endcase
    end
  endfunction

  //----------------------------------------------------------------------
  // Immediates
  //----------------------------------------------------------------------

  logic [31:0] inst_unused;

  function [31:0] imm_i
  (
    input [31:0] inst
  );
    inst_unused = inst;
    return { {20{inst[31]}}, inst[31:20] };
  endfunction

  function [31:0] imm_s
  (
    input [31:0] inst
  );
    inst_unused = inst;
    return { {20{inst[31]}}, inst[31:25], inst[11:7] };
  endfunction

  function [31:0] imm_b
  (
    input [31:0] inst
  );
    inst_unused = inst;
    return { {19{inst[31]}}, inst[31], inst[7], inst[30:25], inst[11:8], 1'b0 };
  endfunction

  function [31:0] imm_j
  (
    input [31:0] inst
  );
    inst_unused = inst;
    return { {11{inst[31]}}, inst[31], inst[19:12], inst[20], inst[30:21], 1'b0 };
  endfunction

  //----------------------------------------------------------------------
  // Instruction Semantics
  //----------------------------------------------------------------------

  logic [31:0] pc;

  task automatic step();
    logic [31:0] pc_next;
    logic [31:0] inst;
    logic  [4:0] rd;
    logic  [4:0] rs1;
    logic  [4:0] rs2;

    if ( !rst ) begin
      inst = imem_rd( pc );
      rd   = inst[`TINYRV1_INST_RD];
      rs1  = inst[`TINYRV1_INST_RS1];
      rs2  = inst[`TINYRV1_INST_RS2];

      pc_next     = pc + 4;
      trace_val   = 1'b1;
      trace_pc    = pc;
      trace_inst  = inst;
      trace_wen   = 1'b0;
      trace_wreg  = 'x;
      trace_wdata = 'x;

      casez ( inst )

        `TINYRV1_INST_ADDI: rf_wr( rd, R[rs1] + imm_i(inst) );
        `TINYRV1_INST_ADD:  rf_wr( rd, R[rs1] + R[rs2] );
        `TINYRV1_INST_MUL:  rf_wr( rd, R[rs1] * R[rs2] );

        `TINYRV1_INST_LW:   rf_wr( rd, dmem_rd( R[rs1] + imm_i(inst) ) );
        `TINYRV1_INST_SW:   dmem_wr( R[rs1] + imm_s(inst), R[rs2] );

        `TINYRV1_INST_JAL:
        begin
          rf_wr( rd, pc + 4 );
          pc_next = pc + imm_j(inst);
        end

        `TINYRV1_INST_JR:
          pc_next = R[rs1];

        `TINYRV1_INST_BNE:
        begin
          if ( R[rs1] != R[rs2] )
            pc_next = pc + imm_b(inst);
        end

      endcase

      pc = pc_next;
    end
  endtask

  //----------------------------------------------------------------------
  // Reset
  //----------------------------------------------------------------------

  always @( posedge clk ) begin
    if ( rst ) begin
      trace_val <= 1'b0;
      pc        <= '0;
      R[0]      <= '0;
      out0      <= '0;
      out1      <= '0;
      out2      <= '0;
      out3      <= '0;
    end
  end

endmodule

`endif /* PROC_FL_V */
