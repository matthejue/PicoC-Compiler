#pragma once

struct mutex {
    int lock;
    int id;
};

int testset(int *lock_addr);
void mutex_init(struct mutex *m);
void mutex_lock(struct mutex *m);
void mutex_unlock(struct mutex *m);

void sleep(int id);
void wakeup(int id);

int testset(int *lock_addr) {
    int old;

    asm("LOADIN BAF IN2 -2");
    asm("TSL IN2 ACC 0");
    asm("STOREIN BAF ACC -3");
    return old;
}

void mutex_init(struct mutex *m) {
    m->lock = 0;
    m->id = (int)m;
    return;
}

void sleep(int id) {
    asm("LOADIN BAF ACC -2");
    asm("INT 4");
    return;
}

void wakeup(int id) {
    asm("LOADIN BAF ACC -2");
    asm("INT 5");
    return;
}

void mutex_lock(struct mutex *m) {
    while (testset(&(m->lock))) {
        sleep(m->id);
    }
    return;
}

void mutex_unlock(struct mutex *m) {
    m->lock = 0;
    wakeup(m->id);
    return;
}
