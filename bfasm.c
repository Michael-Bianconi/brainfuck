//
//  bfasm.c
//  
//
//  Created by Michael Bianconi on 10/5/25.
//
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

/**
 * Appends multiple operates into a single operation.
 * Does not free the operations used.
 *
 * @param numop Number of elements in ops.
 * @param ops Operations to combine.
 * @returns Dynamically allocated array that contains the new operation.
 */
char* multiop(int numop, char* ops) {
  int length = 0;
  for (int i = 0; i < numop; i++) {
    length += strlen(ops[i]);
  }
  char* retval = calloc(length + 1, sizeof(char));
  for (int i = 0; i < numop; i++) {
    strcar(retval, ops[i]);
  }
  return retval;
}

char* op_set(x) {
  char[] set0 = "[-]";
  char* add = op_add(x);
  char*[] ops = char* {set0, add};
  char* retval = multiop(2, {}
}

char* op_add(x) {
  char* op = calloc(x+1, sizeof(char));
  for (int i = 0; i < x; i++) {
    op[i] = '+';
  }
  op[i] = '\0';
  return op;
}

char* op_sub(x) {
  char* op = calloc(x+1, sizeof(char));
  for (int i = 0; i < x; i++) {
    op[i] = '-';
  }
  op[i] = '\0';
  return op;
}

int main(int agrc, char* argv[]) {
  
  
  
  return 0;
}
