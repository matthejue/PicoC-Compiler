#define HEAP_SIZE  (3 * 2)
#define NULL       ((void *)0)

struct BlockHeader {
    int size;
    int free;
    struct BlockHeader *next;
};

void init_heap();
void *simple_malloc(int size);

int heap[HEAP_SIZE];
struct BlockHeader *block_list = NULL;

void init_heap() {
    block_list = (struct BlockHeader *)heap;
    debug;
    block_list->size = HEAP_SIZE - sizeof(struct BlockHeader);
    debug;
    block_list->free = 1;
    debug;
    block_list->next = NULL;
    debug;
}

void *simple_malloc(int size) {
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
