# Vexi Virtual Machine (VVM) Codebook

This document describes the bytecode instruction set for the Vexi Virtual Machine (VVM).
All opcodes and arguments are expected to be in hexadecimal format (e.g., `0x10`).

## 1. Arithmetic Operations

| Opcode (Hex) | Opcode (Dec) | Mnemonic | Description                  | Arguments (Hex)                         |
|--------------|--------------|----------|------------------------------|-----------------------------------------|
| `0x10`       | 16           | `ADD`    | Add source to destination    | `dest_var_opcode, src_val_or_var_opcode` |
| `0x11`       | 17           | `SUB`    | Subtract source from destination | `dest_var_opcode, src_val_or_var_opcode` |
| `0x12`       | 18           | `MUL`    | Multiply destination by source | `dest_var_opcode, src_val_or_var_opcode` |
| `0x13`       | 19           | `DIV`    | Divide destination by source | `dest_var_opcode, src_val_or_var_opcode` |
| `0x14`       | 20           | `MOD`    | Modulo destination by source | `dest_var_opcode, src_val_or_var_opcode` |

## 2. Logic Operations

| Opcode (Hex) | Opcode (Dec) | Mnemonic | Description                  | Arguments (Hex)                                 |
|--------------|--------------|----------|------------------------------|-------------------------------------------------|
| `0x20`       | 32           | `EQ`     | Equal to (sets dest to 1 if true, 0 otherwise) | `dest_var_opcode, val1_or_var_opcode, val2_or_var_opcode` |
| `0x21`       | 33           | `NEQ`    | Not Equal to                 | `dest_var_opcode, val1_or_var_opcode, val2_or_var_opcode` |
| `0x22`       | 34           | `GT`     | Greater Than                 | `dest_var_opcode, val1_or_var_opcode, val2_or_var_opcode` |
| `0x23`       | 35           | `LT`     | Less Than                    | `dest_var_opcode, val1_or_var_opcode, val2_or_var_opcode` |
| `0x24`       | 36           | `GTE`    | Greater Than or Equal To     | `dest_var_opcode, val1_or_var_opcode, val2_or_var_opcode` |
| `0x25`       | 37           | `LTE`    | Less Than or Equal To        | `dest_var_opcode, val1_or_var_opcode, val2_or_var_opcode` |
| `0x26`       | 38           | `AND`    | Logical AND                  | `dest_var_opcode, val1_or_var_opcode, val2_or_var_opcode` |
| `0x27`       | 39           | `OR`     | Logical OR                   | `dest_var_opcode, val1_or_var_opcode, val2_or_var_opcode` |
| `0x28`       | 40           | `NOT`    | Logical NOT                  | `dest_var_opcode, val_or_var_opcode`            |

## 3. Variable Operations

| Opcode (Hex) | Opcode (Dec) | Mnemonic | Description                  | Arguments (Hex)                         |
|--------------|--------------|----------|------------------------------|-----------------------------------------|
| `0x30`       | 48           | `var_i`  | Generic counter variable     | `initial_value`                         |
| `0x31`       | 49           | `var_x`  | Generic numeric variable     | `initial_value`                         |
| `0x32`       | 50           | `var_y`  | Generic numeric variable     | `initial_value`                         |
| `0x33`       | 51           | `var_z`  | Generic numeric variable     | `initial_value`                         |
| `0x34`       | 52           | `var_temp` | Temporary variable         | `initial_value`                         |
| `0x35`       | 53           | `var_mov` | Move/copy variable (moves src to dest) | `dest_var_opcode, src_var_opcode`       |

## 4. Data Structure Operations

| Opcode (Hex) | Opcode (Dec) | Mnemonic | Description                  | Arguments (Hex)                                     |
|--------------|--------------|----------|------------------------------|-----------------------------------------------------|
| `0x50`       | 80           | `ARRAY`  | Initializes an array         | `var_name_str, size_int, default_value_int`         |
| `0x60`       | 96           | `PUSH`   | Pushes value to array        | `array_var_opcode, value_or_var_opcode`             |
| `0x61`       | 97           | `POP`    | Pops value from array        | `array_var_opcode`                                  |
| `0x62`       | 98           | `GET`    | Gets value from array by index | `array_var_opcode, index_val_or_var_opcode, dest_var_opcode` |
| `0x63`       | 99           | `SET`    | Sets value in array by index | `array_var_opcode, index_val_or_var_opcode, value_or_var_opcode` |
| `0x64`       | 100          | `LENGTH` | Gets length of array         | `array_var_opcode, dest_var_opcode`                 |

## 5. I/O Operations

| Opcode (Hex) | Opcode (Dec) | Mnemonic | Description                  | Arguments (Hex)                         |
|--------------|--------------|----------|------------------------------|-----------------------------------------|
| `0x71`       | 113          | `PRINT_VAR` | Print variable's value       | `var_opcode`                            |

## 6. Control Flow Operations

| Opcode (Hex) | Opcode (Dec) | Mnemonic | Description                  | Arguments (Hex)                                     |
|--------------|--------------|----------|------------------------------|-----------------------------------------------------|
| `0x81`       | 129          | `JMP`    | Unconditional jump           | `target_pc`                                         |
| `0x82`       | 130          | `JMP_IF_EQ` | Jump if equal              | `val1_or_var_opcode, val2_or_var_opcode, target_pc` |
| `0x83`       | 131          | `JMP_IF_NEQ` | Jump if not equal           | `val1_or_var_opcode, val2_or_var_opcode, target_pc` |
