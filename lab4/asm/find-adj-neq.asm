#=========================================================================
# find-adj-neq
#=========================================================================
# Search an array in memory to find the first pair of consecutive
# elements that are not equal. Set registers x6 and x7 to the values
# of these two elements, or 99 if no such pair exists. The pseudocode
# is shown below.
#
#   a = [ 7, 7, 7, 7, 9, 9, 9, 4 ]
#   n = 8
#
#   first  = 99
#   second = 99
#   for i in range(n-1):
#     if ( a[i] != a[i+1] ):
#       first  = a[i]
#       second = a[i+1]
#       break
#

.text
  addi x1, x0, 256        # a array
  addi x2, x0, 7          # need n-1 comparisons
  addi x6, x0, 99         # first = 99
  addi x7, x0, 99         # second = 99

  #''' DISCUSSION TASK '''''''''''''''''''''''''''''''''''''''''''''''''''
  # Implement the loop
  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

done:
  jal  x0, done

.data
  .word 7
  .word 7
  .word 7
  .word 7
  .word 9
  .word 9
  .word 9
  .word 4

