# GETI

`GETI @TOP @TOP @TOP`

## ALGORITHM

**INITIAL STATE:**

```text
1. Modify the address count from the right instead of the left.
   Example: If address 4 is provided, and the data pointer is at 10,
   then the new address is 6 (10 - 4).
1. Shift a0 and a1 right by 2 cells, then duplicate them and move
   the data pointer back 2 cells
2. Move the rightmost 16-bit value (tape[5] and tape[6], initially)
   into the two zeroed cells after the rightmost address. Then, shift
   both addresses left. Subtract two from the rightmost address.
   Repeat this until the rightmost address is 0, which indicates
   the next value on the tape is the one at the desired address.
3. Copy that value into the space where the rightmost address used
   to be (now zero).


Let a=4 and d=10, so a becomes 6.

0   1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  16  17
----------------------------------------------------------------------
0   1   2   3   4   5   6   7   8   9   6   2   0<  0   0   0   0   0  # Initial state
0   1   2   3   4   5   6   7   8   9   0   0   6   2   6   2<  0   0  # Step 1
0   1   2   3   4   5   6   7   0   0   6   0   4<  0   0   0   4   5  # Step 2
0   1   2   3   4   5   6   7   0   0   6   0   4<  0   0   0   8   9  # Step 2
0   1   2   3   4   5   0   0   6   0   2<  0   0   0   6   7   8   9
0   1   2   3   0   0   6   0   0<  0   0   0   4   5   6   7   8   9  

```