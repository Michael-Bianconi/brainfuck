# Brainfuck Assembly (.bfa)

## Grammar

```
PROGRAM = (INSTRUCTION PROGRAM) | INSTRUCTION 
INSTRUCTION = LABEL MNEMONIC OPERANDS | MNEMONIC OPERANDS
LABEL = ALPHANUMERIC
MNEMONIC = ALPHANUMERIC
OPERANDS = OPERAND OPERANDS | NONE | OPERAND
OPERAND = IMMEDIATE | REGISTER | LABEL | NATIVE
IMMEDIATE = NUMERIC | HEXADECIMAL
REGISTER = $c0 | $c1 | $v0 | $v1 | $pc | $sp
NATIVE = []+-<>,.
```

## Instructions

### LOAD $sp imm

Push the immediate value onto the stack.

### LOAD $rt imm

Set register to immediate value.

### LOAD $rt $rs

Set $rt to $rs

### GETI $sp $sp

Pop an address off the stack. Locate the 16-bit value at that address.
Push it onto the stack.

### GETI $rt $rs

Fetch an address from register $rs. Locate the 16-bit value at that address.
Move it into $rt

### SETI $sp $sp

Pop an address off the stack. Pop a value off the stack. Move that value
to the memory location at that address.

### SETI $rt $rs

Fetch a value from $rs. Fetch an address from $rt. Set the memory location
at that address to the value.