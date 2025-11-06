# brainfuck interpreter

This is a brainfuck interpreter, written in C.

```
$ gcc brainfuck.c -o brainfuck
$ ./brainfuck test/HelloWorld.bf
```

# bfasm compiler

## Registers

### General Registers
There are 32 8-bit registers, which are stored in the first 32 bytes of memory.
These are denoted by a dollar sign followed by the ID of the register, which is in the range 0-31.
The first register is $0, the next is $1, the next is $2, and so on. These are general-use
registers.

### Temporary Register
There is one temporary register, $t. This register is modified internally by some BFASM operations.
It may not be used by the user. Note: The $t register is guaranteed to hold the value 0 at the
beginning and end of every BFASM operation.


### The data pointer ($d)
The data pointer, referred to as $d, jumps around to the area of memory required. After it moves
to a memory cell and the desired operation is performed, it always resets back to 0.

### The zero pointer ($0)
The zero pointer $0 points to a memory cell that is always zero.

## Functions

Functions in BFASM are snippets of code that are copied, inline, where ever
they are used.

### DATA

A no argument instruction that tells the assembler to begin memory cell
allocation. If the DATA instruction is present, it must be the first
instruction in the source file.

### ALOC name n

Allocates n memory cells and leaves them zero-filled.

### TEXT

A no argument instruction that tells the assembler to end memory cell
allocation and begin proper instruction encoding. TEXT can appear anywhere,
even multiple times. However, it is a noop if executed multiple times, or
if there is no DATA instruction prior.

### BYTE name x
Creates a memory cell that can be referenced through $name and initializes
it with value x.

### DSTR name "string"
Creates a block of memory cells that hold the characters in "string", plus
and additional cell that holds the value zero.

### DARR name n
Creates a block of memory cells n-long.

## Internal operations
Internal instructions are not meant to be used when writing a BFASM application. They
directly modify the underlying structures in memory. Several pseudo-instructions rely
on those underlying structures remaining in a very precise state. If using internal
instructions, the follow guidelines should be followed:
1. The data pointer must be at position 0 when a pseudo-instruction is called. This means
if `MOVE n` is used, there must be a corresponding `MOVE -n` to reset its position.
2. Temporary registers must equal 0 before a pseudo-instruction is used.
3. If the value at the top of the stack is used as a temporary variable that is reduced to 0,
`popn` should be used to fix the stack pointer.

### MOVE x
Moves the data pointer x cells. If x is positive, moves right. If x is negative, moves left.

**Note:** When the operand for this operation is represented as (m-n), that
should be read as moving from $n to $m.

### _RES
The memory cell pointed at by the data pointer $d is set to 0.

### _ADD x
The memory cell at the data pointer $d is incremented by x. If this
results in the memory cell overflowing, sets carry flag $c to 1.
Otherwise, carry flag $c is set to 0.

### _SUB x
The memory cell at the data pointer $d is decremented by x.

**Implementation:** `-` times x (potentially optimized)

### \_NEZ ... \_END
The enclosed operations are performed until the memory cell
at $d (which may change depending on the enclosed operations)
is equal to zero.

**Implementation:** `[...]`

### _LIN x

Load x bytes from stdin into the current and proceeding x memory cells.

**Validations:**
1. `x` must be greater than zero.

**Effects:**
1. The next `x` memory cells, starting at the current memory cell, are filled from stdin.
2. The data pointer is moved right `x` cells.

### _OUT x

Prints the contents of the next `x` memory cells, starting with the current
cell.

**Effects:**
1. The contents of the next `x` memory cells are printed to stdout.
2. The data pointer is moved right `x` cells.


## Arithmetic

### SETI $n x
Sets the specified register to the immediate value of x.
Does not modify temporary registers.

### SETR $n $m
Sets $n to the value in $m. Modifies temporary registers.

### ADDI $n x
Adds to the specified register the value of x.

### ADDA $n $m
Adds to register n the value of register $m.

### SUBI $n x
Subtracts from the specified register the value of x.

### SUBA $n $m
Subtracts from $n the value at address $m.

### MULT $n x
Multiplies $n by immediate value x.

## Boolean Logic

### LNOT $n $m
Logical not. Sets $n to 0 if $m is non-zero. Set $n to 1 if $m is zero.
$n and $m may be the same address.

## Logic Flow

### .function name ... .return

Creates function name(), which encloses several instructions. When
the function is referenced, the enclosed instructions are copied in.
1. Each function must have exactly one return
2. A function may not be defined within another function
3. The stack and stack pointer must be identical entering the function as leaving it

**Implementation:** N/A

### JMP func
Executes the specified function.

**Implementation:**
```
func()
```

### JNZ $n func
Executes the specified function if $n is non-zero.

**Implementation:**
```
MOVE n
_NEZ
  MOVE -n
  func()
  MOVE $0
_END
MOVE -$0
```

## I/O

### OUTC n m

Navigates to memory cell n and prints the contents of the next m cells.

