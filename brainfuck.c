#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>

/**
 * Reads the file at the given path into a char buffer.
 * Remember to free the returned buffer.
 *
 * Program exits if file does not exist, or if unable to be read.
 *
 * @param filepath Path to the file.
 */
char* loadsource(const char* filepath) {

  FILE *fp = fopen (filepath, "rb");  // File pointer for source file
  long size;                          // Size of source file
  char *buffer;                       // Holds source file contents

  if (!fp) {
    perror(filepath);
    exit(1);
  }

  fseek(fp, 0L, SEEK_END);
  size = ftell(fp);
  rewind(fp);

  buffer = calloc(1, size+1);
  if (!buffer) {
    fclose(fp);
    fputs("Memory allocation for source file failed", stderr);
    exit(1);
  }

  if (fread(buffer, size, 1, fp) != 1) {
    fclose(fp);
    free(buffer);
    fputs("Reading source file failed", stderr);
    exit(1);
  }

  fclose(fp);
  return buffer;
}

/**
 * Determines where the iptr should land when jumping.
 * If the character at iptr is '[', jumps forward.
 * If the character at iptr is ']', jumps backward.
 * Jumps to the enclosing bracket, ignoring any nested brackets.
 *
 * @param iptr The current position of the instruction pointer. Should point to a '[' or ']'.
 * @return A pointer to the address the jump should land on.
 */
char* jump(char* iptr) {
  int dir = *iptr == '[' ? 1 : -1;  // Direction of jump
  int bracketcounter = dir;         // Tracks nested brackets
  iptr += dir;

  while (bracketcounter != 0) {
    if (*iptr == '[') {
      bracketcounter++;
    } else if (*iptr == ']') {
      bracketcounter--;
    }
    iptr += dir;
  }

  return iptr -= dir;
}

/**
 * Executes brainfuck source code.
 * Modifies the contents of the data parameter. Prints program output to stdout.
 *
 * @param iptr Instruction pointer, pointed at the start of the source code.
 * @param dptr Data pointer, pointed at the start of the memory block.
*/
void run(char* iptr, uint8_t* dptr) {
  while (*iptr != '\0') {
    switch (*iptr) {
      case '[': if (*dptr == 0) iptr = jump(iptr); break;
      case ']': if (*dptr != 0) iptr = jump(iptr); break;
      case '+': (*dptr)++; break;
      case '-': (*dptr)--; break;
      case '>': dptr++; break;
      case '<': dptr--; break;
      case '.': printf("%c", *dptr); break;
      case ',': scanf("%c", dptr); break;
    }
    iptr++;
  }
  printf("\n");
  return;
}

/**
 * Interprets and executes a brainfuck sourcefile.
 */
int main(int argc, char* argv[]) {
  int opt;              // Reads command line arguments
  int memsize = 30000;  // Size of program data block
  char* sourcefile;     // Path to the .bf source code file
  char* iptr;           // Instruction pointer
  uint8_t* dptr;        // Data pointer
  
  while ((opt = getopt(argc, argv, "x:h")) != -1) {
      switch (opt) {
        case 'p':
          sourcefile = optarg;
          break;
        case 'x':
          memsize = atoi(optarg);
          break;
        case 'h':
        default:
          fprintf(stderr, "Usage: %s [-x memsize] sourcefile \n", argv[0]);
          fprintf(stderr, "  -x memsize: Size of memory allocation (bytes), default %d\n", memsize);
          fprintf(stderr, "  sourcefile: Path to .bf file\n");
          exit(1);
      }
  }
  
  if (optind >= argc) {
       fprintf(stderr, "Missing sourcefile, use -h for help\n");
       exit(1);
   }

  sourcefile = argv[optind];
  iptr = loadsource(sourcefile);
  dptr = (uint8_t*) malloc(memsize * sizeof(uint8_t));
  run(iptr, dptr);
  free(iptr);
  free(dptr);

  return 0;
}
