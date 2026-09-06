# BFX

BFX (Brainfuck Extended) is a variant of Brainfuck that directly transpiles
into Brainfuck. It provides quality-of-life features and the BFX transpiler
can perform some optimizations as well. All Brainfuck programs are also
valid BFX programs.

Within BFASM, BFX is used as an intermediary when compiling BFASM into
Brainfuck.

## INSTRUCTIONS

* `>{x}` Shift the data pointer right by `x` cells, where `x` is a positive integer. If `x` is omitted,
shift right by 1.
* `<{x}` Shift the data pointer left by `x` cells, where `x` is a positive integer. If `x` is omitted,
shift left by 1.
* `+{x}` Add `x` to the current cell. If `x` is omitted, add 1.
* `-{x}` Subtract `x` from the current cell. If `x` is omitted, subtract 1.
* `={x}` Set the current cell to `x`. If `x` is omitted, set to 0.
