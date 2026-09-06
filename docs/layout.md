# LAYOUT

The memory layout in any Brainfuck program is of critical importance.

A pure Brainfuck program has a single, infinitely long memory tape.
Each cell in the tape is 8-bits wide, unsigned (allowing values 0-255).
Each cell is initialized to 0, and the Data Pointer starts at 0.

## 16-BIT

BFOS is a 16-bit system, and so Brainfuck's 8-bit cells must be aggregated
to accommodate the increased width. There are many pre-established methods
for doing so, but most involve padding the values with empty cells for
carry flags and temporary storage. BFOS performs all operations on the
stack (more on that later), and so it is wasteful to store these extra
cells on every value. Rather, when we must manipulate a 16-bit value,
we pull it to the top of the stack and use the stack-space for temporary
storage.

```text
[B0 B1]
```

BFOS's 16-bit values are stored in two cells in little-endian format.