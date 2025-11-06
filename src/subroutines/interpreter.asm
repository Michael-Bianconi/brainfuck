# Requirements:
#
# $prog is an allocated memory chunk.
# The first memory cells in $prog contain only valid brainfuck instructions.
# The remaining memory cells contain only zero values. $prog is sufficiently large such that
# the allocated memory is enough to both store the program and execute it.
#
# The data pointer is at page 0.
#
# Decimal values of Brainfuck instructions:
# ] 93
# [ 91
# > 62
# < 60
# . 46
# - 45
# , 44
# + 43
# ! 33
#
# CORE CONCEPT:
# The allocated memory is utilized as follows:
# [r][i][source]0[data * 2]
r=2
c=0
i=>
[0 [>[>]]] [-] |

+: If r is 0, iptr = 0. {dptr+1} += 1
-: Move to data pointer + 1, sub 1
,: Move to data pointer + 1, read 1
.: Move to data poonter + 1, output 1
>: Move to data pointer, set to 0. Move right 2, set to 1.
<: Move to data pointer, set to 1. Move left 2, set to 1.
[: Move to data pointer. If dptr+1 is 0
d: Start of data block

ALOC $bracketcounter 1

.FUNCTION gotodptr
    # Moves true data pointer from text block into data block, finds active
    # memory cell.
    _FND 33 1   # Find start of data block
    _FND 1 2    # Find active memory cell
    MOVE 1      # Move to data cell

.FUNCTION gotoiptr
    # Moves true data pointer from data block into text block, finds active
    # instruction cell.
    MOVE -1     # Move data pointer to dptr flag
    MOVE 33 -2  # Find

.FUNCTION >
    CALL gotodptr
    MOVE -1
    _SUB 1
    MOVE 2
    _ADD 1
    MOVE -1
    CALL gotoiptr

.FUNCTION <
    CALL gotodptr
    MOVE -1
    _SUB 1
    MOVE -2
    ADD 1
    MOVE 1
    CALL gotoiptr

.FUNCTION
