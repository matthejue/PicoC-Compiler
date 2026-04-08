#pragma once

#define HEAP_SIZE  (5 * 4)     // heap size in words
#define NULL       ((void *)0)

struct BlockHeader {
    int size;                      // usable words in this block
    int free;                      // 1 = free, 0 = used
    struct BlockHeader *next;      // pointer to next block
};

void init_heap();
void *malloc(int size);
void free(void *ptr);

int heap[HEAP_SIZE];                  // fixed-size heap memory
struct BlockHeader *block_list = NULL; // head of the block list (free + used)

// Merge adjacent free blocks
void merge_free_blocks() {
    struct BlockHeader *current = block_list;

    while (current != NULL && current->next != NULL) {
        if (current->free == 1 && current->next->free == 1) {
            // Merge them (always contiguous in this model)
            current->size = current->size + sizeof(struct BlockHeader) + current->next->size;
            current->next = current->next->next;
        } else {
            current = current->next;
        }
    }
}

// Initialize heap: one large free block
void init_heap() {
    block_list = (struct BlockHeader *)heap;
    block_list->size = HEAP_SIZE - sizeof(struct BlockHeader);
    block_list->free = 1;
    block_list->next = NULL;
}

// Allocate memory
void *malloc(int size) {
    struct BlockHeader *current = block_list;

    while (current != NULL) {
        if (current->free == 1 && current->size >= size) {

            // Split if there’s enough room for another block
            if (current->size >= size + sizeof(struct BlockHeader) + 1) {
                struct BlockHeader *new_block =
                    (struct BlockHeader *)((int *)(current + 1) + size);

                new_block->size = current->size - size - sizeof(struct BlockHeader);
                new_block->free = 1;
                new_block->next = current->next;

                current->size = size;
                current->next = new_block;
            }

            current->free = 0;
            return (void *)(current + 1);
        }

        current = current->next;
    }

    return NULL;
}

// Free a block and merge neighbors
void free(void *ptr) {
    if (ptr == NULL)
        return;

    struct BlockHeader *header = (struct BlockHeader *)ptr - 1;
    header->free = 1;

    merge_free_blocks();
}
