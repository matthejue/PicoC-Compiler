int printf(char *format);
int scanf(char *format, int *value);

int frame_base() {
    asm("MOVE BAF ACC");
    return 0;
}

int uart_print_integer(int value) {
    asm("LOADIN BAF ACC -2");
    asm("INT 0");
    return 0;
}

int uart_print_string(char *value) {
    asm("LOADIN BAF ACC -2");
    asm("INT 1");
    return 0;
}

int uart_read_word() {
    asm("INT 2");
    return 0;
}

int uart_print_character(int value) {
    char character[2];

    character[0] = value;
    character[1] = 0;
    uart_print_string(character);
    return 0;
}

int input_character_at(int packed, int index) {
    if (index == 0) {
        return packed / 16777216;
    }

    if (index == 1) {
        return (packed / 65536) & 255;
    }

    if (index == 2) {
        return (packed / 256) & 255;
    }

    return packed & 255;
}

int is_decimal_digit(int value) {
    if (value < 48) {
        return 0;
    }

    if (value > 57) {
        return 0;
    }

    return 1;
}

int parse_decimal_input(int packed, int *value) {
    int index;
    int current;
    int sign;
    int has_digit;
    int decimal_digit;

    sign = 1;
    has_digit = 0;
    index = 0;

    current = input_character_at(packed, 0);
    if (current == 45) {
        sign = -1;
        index = 1;
    }

    while (index < 4) {
        current = input_character_at(packed, index);
        decimal_digit = is_decimal_digit(current);

        if (decimal_digit == 0) {
            index = 4;
        } else {
            *value = (*value * 10) + (current - 48);
            has_digit = 1;
            index = index + 1;
        }
    }

    if (has_digit == 0) {
        return 0;
    }

    *value = (*value) * sign;
    return 1;
}

int next_printf_argument(int argument_index) {
    int *base;
    int slot;

    base = (int *)frame_base();
    slot = argument_index + 3;
    return *(base - slot);
}

int printf(char *format) {
    int index;
    int current;
    int argument_index;
    int argument_value;

    index = 0;
    argument_index = 0;

    while (format[index] != 0) {
        current = format[index];

        if (current == 37) {
            index = index + 1;
            current = format[index];

            if (current == 100) {
                argument_value = next_printf_argument(argument_index);
                uart_print_integer(argument_value);
                argument_index = argument_index + 1;
            } else {
                if (current == 99) {
                    argument_value = next_printf_argument(argument_index);
                    uart_print_character(argument_value);
                    argument_index = argument_index + 1;
                } else {
                    if (current == 37) {
                        uart_print_character(37);
                    }
                }
            }
        } else {
            uart_print_character(current);
        }

        index = index + 1;
    }

    return 0;
}

int scanf(char *format, int *value) {
    int packed;
    int current;

    if (format[0] != 37) {
        return 0;
    }

    if (format[2] != 0) {
        return 0;
    }

    current = format[1];
    packed = uart_read_word();

    if (current == 99) {
        *value = input_character_at(packed, 0);
        return 1;
    }

    if (current == 100) {
        *value = 0;
        return parse_decimal_input(packed, value);
    }

    return 0;
}
