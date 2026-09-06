# BFCode

BFCode is a simple programming language that compiles into brainfuck.

## Variables

### uint_8
uint_8 (unsigned integer 8-bits) is the only true data type. Under the hood, all other data types
operate on uint_8 data.
```c
uint_8 a;                   //  Allocates one 8-bit value on the heap, initialized to 0.
uint_8 a = 5;               //  Allocates one 8-bit value on the heap, initialized to 5.
uint_8 a = 'a';             //  Allocates one 8-bit value on the heap, initialized to 97.
uint_8 a[5];                //  Allocates five 8-bit values on the heap, initialized to 0.
uint_8 a[] = {1, 2, 3};     //  Allocates three 8-bit values on the heap, initialized to 1, 2, 3.
uint_8 a[] = {1, 'a', 3};   //  Allocates three 8-bit values on the heap, initialized to 1, 97, 3.
uint_8 a[] = "abc";         //  Allocates four 8-bit values on the heap, initialized to 97, 98, 99, 0.
uint_8 a = true;            //  Allocates one 8-bit value on the heap, initialized to 1.
uint_8 a = false;           //  Allocates one 8-bit value on the heap, initialized to 0.
```

### pointer
Pointers hold the addresses of other variables. By default, pointers are uint_16s. Note
that pointers are still typed. A pointer to a uint_8 variable will still be 16-bits.
```c
uint_8 a = 5;               // Allocates a at memory address 0x0A5C
uint_8 *b = &a;             // Allocates b and initializes it to 0x0A5C
```

### Assignment
```c
uint_8 a = 5;               // Allocates a=5 on the heap
uint_8 b = 3;               // Allocates b=3 on the heap
a = 10;                     // Sets a to 10
a = b;                      // Sets a to 3
a[3] = 10;                  // Sets the value at &a + 3 to 10.
```

## Functions

```c
uint_8 plus(uint_8 a, uint_8 b) {
    return 
}
```