#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define BUFFER_SIZE 1000
#define on_error(...) { fprintf(stderr, __VA_ARGS__); fflush(stderr); exit(1); }

void echo(char *arg1, char *arg2){
     char result[BUFFER_SIZE*2];
     char input1[BUFFER_SIZE];
     char input2[BUFFER_SIZE];

     strncpy(input1, arg1, BUFFER_SIZE);
     strncpy(input2, arg2, BUFFER_SIZE);
     strcat(result, input1);
     strcat(result, input2);
     printf("Echo Response: %s\n", result);
}

int main(int argc, char **argv){
    if (argc < 3) on_error("Usage: %s [argument1] [argument2]\n", argv[0]);
    echo(argv[1], argv[2]);
    return 0;
}