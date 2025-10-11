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
if `_MOV n` is used, there must be a corresponding `_MOV -n` to reset its position.
2. Temporary registers must equal 0 before a pseudo-instruction is used.

### _MOV x
Moves the data pointer x cells.

**Implementation:** `>` times x if x > 0, or `<` if x < 0

**Note:** When the operand for this operation is represented as (m-n), that
should be read as moving from $n to $m.

### _RES
The memory cell pointed at by the data pointer $d is set to 0.

**Implementation:** `[-]`

### _ADD x
The memory cell at the data pointer $d is incremented by x.

**Implementation:** `+` times x (potentially optimized)

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

### ADD $n x
Adds to the specified register the value of x.
Overflow behavior depends on the interpreter.
Does not modify temporary registers.

### ADD $n $m
Adds to register n the value of register $m. Modifies temporary registers.

### SUB $n x
Subtracts from the specified register the value of x. Underflow behavior depends on the interpreter.

### SUB $n $x

### MUL $n $x

## Boolean Logic

### EQL $n x
Sets $n to 1 if $n is equal to x. Otherwise sets $n to 0.

**Implementation:**
```
_MOV n
_SUB (x-1)



```

5-10 = 250
10-10 = 0


### EQL $n $m
Sets $n to 1 if $n is equal to $m. Otherwise sets $n to 0.

**Implementation:**
```
_MOV n
_NEZ
  _MOV (t1-n)
  _ADD 1
  _MOV (n-t1)
  _SUB 1
_END
_ADD 1
_MOV (m-t1)
_NEZ
  _MOV (t1-m)
  _SUB 1
  _MOV (t0-t1)
  _ADD 1
  _MOV (m-t0)
  _SUB 1
_END
_MOV (t0-m)
_NEZ
  _MOV (m-t0)
  _ADD 1
  _MOV (t0-m)
  _SUB 1
_END
_MOV (t1-t0)
_NEZ
  _MOV (n-t1)
  _SUB 1
  _MOV (t1-n)
  _RES
_END
```

### NEQ $n $m


## Logic Flow

### FUNC name ... RET

Creates function name(), which encloses several instructions. When
the function is referenced, the enclosed instructions are copied in.

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
_MOV n
_NEZ
  _MOV -n
  func()
  _MOV $0
_END
_MOV -$0
```

## I/O

### OUTC n m

Navigates to memory cell n and prints the contents of the next m cells.

