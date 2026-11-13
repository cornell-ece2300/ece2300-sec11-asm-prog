#=========================================================================
# find-adj-eq
#=========================================================================
# Search an array in memory to find the first pair of consecutive
# elements that are equal. Set register x6 to the value of the equal
# elements, or 99 if no such pair exists. The pseudocode is shown below.
#
#   a = [ 7, 2, 3, 9, 9, 8, 6, 4 ]
#   n = 8
#
#   found = 99
#   for i in range(1,n):
#     if ( a[i] == a[1+1] ):
#       found = a[i]
#       break
#

.text
  addi x1, x0, 256        # a array
  addi x2, x0, 7          # need n-1 iterations
  addi x6, x0, 99         # found = 99

  #''' DISCUSSION TASK '''''''''''''''''''''''''''''''''''''''''''''''''''
  # Implement the loop
  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

done:
  jal  x0, done

.data
  .word 7
  .word 2
  .word 3
  .word 9
  .word 9
  .word 8
  .word 6
  .word 4

