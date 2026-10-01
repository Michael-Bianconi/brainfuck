# Brainfuck Machine Code (.bfm)

Brainfuck Machine Code (BFM or .bfm) is the binary representation of Brainfuck
Assembly Code (BFA or .bfa). Each BFA instruction assembles to a single BFM code,
with the exception of pseudo-instructions, which assemble to multiple BFM codes,
and with the exception of no-op BFA instructions, which assemble into zero BFM
codes.

## Instructions & Opcodes

Each BFA instruction compiles into zero, one, or many BFM instructions.
Each BFM instruction is a 32-bit unsigned integer.

### I-Instructions

I-Instructions utilize a single register and a single immediate value.

- o: The opcode
- d: Destination register
- s: Source register
- i: The 16-bit immediate

```
oooooodd dddsssss iiiiiiii iiiiiiii
```

| Operation | Opcode | Description                                                                                                                    |
|-----------|--------|--------------------------------------------------------------------------------------------------------------------------------|
| LDIL      | 000001 | Load immediate value into register. Moves the 16-bit immediate value into the least significant bits of the provided register. |
| LDIU      | 000010 | Load immediate value       
