# BrainfuckVM

# Overview
BrainfuckVM is a Brainfuck program that can execute .bfm files.

# Memory Layout
BrainfuckVM, being a proper Brainfuck (.bf) program, has access only to
the standard Brainfuck memory tape. As such, it maintains strict (albeit
slightly enigmatic) memory layout.

| Section   | Length                   | Notes                                 |
|-----------|--------------------------|---------------------------------------|
| .bfm      | Equals size of .bfm file | .bfm is loaded directly onto tape     |
| iptr      | 4                        | 32-bit instruction pointer            |
| registers | 128                      | 32 32-bit registers                   |
| stack     | Variable                 | Starts at length 0, then expands      |
| sptr      | 4                        | Always stored at the top of the stack |

```plaintext
[ <.bfm program text> ..., instruction pointer, registers 0-32, stack, stack pointer]
```