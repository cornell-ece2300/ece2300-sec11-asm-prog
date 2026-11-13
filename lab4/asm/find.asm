#=========================================================================
# find-v1
#=========================================================================
# Search an array in memory to find if it contains the value 9. Set
# register x6 to be one if 9 is found and zero otherwise. The pseudocode
# is shown below.
#
#   a = [ 7, 2, 3, 9, 1, 8, 6, 4 ]
#   n = 8
#
#   found = 0
#   for i in range(1,n):
#     if ( a[i] == 9 ):
#       found = 1
#       break
#

.text
  addi x1, x0, 256        # a array
  addi x2, x0, 8          # n = 8
  addi x6, x0, 0          # found = 0

loop:
  lw   x3, 0(x1)          # read a[i]
  addi x4, x0, 9          #
  bne  x3, x4, notfound   # if ( a[i] != 9 ) goto notfound
  addi x6, x0, 1          # found = 1
  jal  x0, done           # goto done

notfound:
  addi x1, x1, 4          # a ptr bump
  addi x2, x2, -1
  bne  x2, x0, loop

done:
  jal  x0, done

.data
  .word 7
  .word 2
  .word 3
  .word 9
  .word 1
  .word 8
  .word 6
  .word 4

