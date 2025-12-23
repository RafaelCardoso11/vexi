# VEXI VVM Codebook (v2 - Raw Byte Format)

This document describes the raw, text-based bytecode format for the VEXI VM. It is designed for maximum token density for LLM generation.

## File Format

- Each line is an instruction: `OPCODE,ARG1,ARG2,...`
- All numeric values, including opcodes, MUST be in hexadecimal format (e.g., `0x10`).
- There are no comments or unnecessary whitespace.
- Strings (like labels for jumps) are used only where necessary.

---

## 1. System Variable Codes

Reserved system variables are not referred to by name, but by a 1-byte hex code.

| Code | Variable Name |
|------|---------------|
| `0x00` | `var_i`       |
| `0x01` | `var_x`       |
| `0x02` | `var_y`       |
| `0x03` | `var_z`       |
| `0x04` | `var_temp`    |

---

## 2. Instruction Set (Opcodes)

### **Arithmetic Operations (0x10 - 0x1F)**
- `0x10` (`ADD`): `0x10,DEST_VAR_CODE,SRC` -> Adds `SRC` to the variable at `DEST_VAR_CODE`. `SRC` can be a variable code or a hex literal.
- `0x11` (`SUB`): `0x11,DEST_VAR_CODE,SRC`
- `0x12` (`MUL`): `0x12,DEST_VAR_CODE,SRC`
- `0x13` (`DIV`): `0x13,DEST_VAR_CODE,SRC`
- `0x14` (`MOD`): `0x14,DEST_VAR_CODE,SRC`

### **Logical Operations (0x20 - 0x2F)**
- `0x20` (`EQ`): `0x20,DEST_VAR_CODE,A,B` -> Sets var at `DEST_VAR_CODE` to 1 if `A == B`, else 0.
- `0x21` (`NEQ`): `0x21,DEST_VAR_CODE,A,B`
- `0x26` (`AND`): `0x26,DEST_VAR_CODE,A,B`
- `0x27` (`OR`): `0x27,DEST_VAR_CODE,A,B`
- `0x28` (`NOT`): `0x28,DEST_VAR_CODE,A`

### **Variable & Memory Operations (0x30 - 0x3F)**
- `0x30` - `0x34`: Direct set. E.g., `0x31,0x64` sets `var_x` (whose internal opcode is `0x31`) to `100`.
- `0x35` (`MOV`): `0x35,DEST_VAR_CODE,SRC_VAR_CODE` -> Copies value from `SRC` to `DEST`.

### **Data Structure Operations (0x50 - 0x6F)**
- `0x50` (`ARRAY`): `0x50,ARRAY_NAME,SIZE,DEFAULT_VALUE` -> Creates an array. `ARRAY_NAME` is a string.
- `0x62` (`GET`): `0x62,ARRAY_NAME,INDEX,DEST_VAR_CODE`
- `0x63` (`ASET`): `0x63,ARRAY_NAME,INDEX,VALUE` -> Sets array element.

### **I/O & Control Flow (Pseudo-Ops)**
These are handled by the interpreter and are not core opcodes. They are an exception to the hex-only rule for the command itself.
- `PRINT_STR,STRING`
- `PRINT_VAR,VAR_CODE`
- `INPUT_INT,VAR_CODE`
- `LABEL,LABEL_NAME`
- `JMP,LABEL_NAME`
- `JMP_IF_EQ,VAR_CODE,VALUE,LABEL_NAME`
- `JMP_IF_NEQ,VAR_CODE,VALUE,LABEL_NAME`