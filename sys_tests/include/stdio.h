/*
 * printf format codes:
 *   0: value is a char* buffer
 *   1: value is a signed decimal integer
 *
 * scanf format codes:
 *   1: read one signed decimal integer from the next 4 UART bytes
 */
int printf(int format, int value);
int scanf(int format, int *value);

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

int unpack_input_char(int packed, int index) {
    int byte0;
    int byte1;
    int byte2;

    byte0 = packed / 16777216;
    packed = packed - (byte0 * 16777216);
    if (index == 0) {
        return byte0;
    }

    byte1 = packed / 65536;
    packed = packed - (byte1 * 65536);
    if (index == 1) {
        return byte1;
    }

    byte2 = packed / 256;
    packed = packed - (byte2 * 256);
    if (index == 2) {
        return byte2;
    }

    return packed;
}

int is_input_terminator(int value) {
    if (value == 0) {
        return 1;
    }

    if (value == 10) {
        return 1;
    }

    if (value == 13) {
        return 1;
    }

    if (value == 32) {
        return 1;
    }

    if (value == 9) {
        return 1;
    }

    return 0;
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

int parse_decimal_word(int packed, int *value) {
    int index;
    int current;
    int sign;
    int parsed;
    int has_digit;
    int terminator;
    int done;
    int decimal_digit;

    sign = 1;
    parsed = 0;
    has_digit = 0;
    done = 0;

    index = 0;
    while (index < 4) {
        if (done) {
            index = 4;
        } else {
            current = unpack_input_char(packed, index);
            terminator = is_input_terminator(current);

            if (terminator) {
                done = 1;
            } else {
                if (parsed == 0) {
                    if (current == 45) {
                        sign = -1;
                        parsed = 1;
                    } else {
                        if (current == 43) {
                            parsed = 1;
                        } else {
                            decimal_digit = is_decimal_digit(current);
                            if (decimal_digit == 0) {
                                return 0;
                            }

                            *value = (*value * 10) + (current - 48);
                            has_digit = 1;
                            parsed = 1;
                        }
                    }
                } else {
                    decimal_digit = is_decimal_digit(current);
                    if (decimal_digit == 0) {
                        return 0;
                    }

                    *value = (*value * 10) + (current - 48);
                    has_digit = 1;
                }

                index = index + 1;
            }
        }
    }

    if (has_digit == 0) {
        return 0;
    }

    *value = (*value) * sign;
    return 1;
}

int printf(int format, int value) {
    if (format == 0) {
        uart_print_string((char *)value);
        return 0;
    }

    if (format == 1) {
        uart_print_integer(value);
        return 0;
    }

    return -1;
}

int scanf(int format, int *value) {
    int packed;

    if (format != 1) {
        return 0;
    }

    *value = 0;
    packed = uart_read_word();
    return parse_decimal_word(packed, value);
}
