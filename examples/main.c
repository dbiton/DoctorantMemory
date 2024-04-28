#include <stdio.h>
#include <stdlib.h>

int main() {
    // Allocate memory for the message
    char *message = (char *)malloc(14 * sizeof(char)); // 14 characters including '\0'

    if (message == NULL) {
        printf("Memory allocation failed\n");
        return 1;
    }

    // Copy the message
    sprintf(message, "Hello, World!");

    // Print the message
    printf("%s\n", message);

    // Free allocated memory
    free(message);

    return 0;
}