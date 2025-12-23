from .tools import TOOLS

class CoreService:
    def __init__(self):
        # Armazena variáveis do Core
        self.variables = dict.fromkeys(TOOLS["variables"].values(), 0)
        self.stack = []

    def _get_value(self, operand):
        if isinstance(operand, str) and operand in self.variables:
            return self.variables[operand]
        return operand

    # -------------------------------
    # Constants handling
    # -------------------------------
    def get_constant(self, *codes):
        """
        Combina múltiplos códigos bytecode para formar valores maiores que 255.
        Ex: get_constant(0xFF, 0x02) -> 255*256 + 2 = 65282
        """
        value = 0
        for c in codes:
            value = (value << 8) + TOOLS["constants"].get(c, c)
        return value

    # -------------------------------
    # Execute a patch (single instruction)
    # -------------------------------
    def exec_patch(self, patch):
        opcode, args = patch
        for group_name, group in TOOLS.items():
            if opcode in group:
                op_name = group[opcode]
                if isinstance(op_name, str):
                    method_name = f"_exec_{op_name.lower()}"
                    if hasattr(self, method_name):
                        if not isinstance(args, (list, tuple)):
                            args = [args]
                        return getattr(self, method_name)(*args)
                    else:
                        # apenas log, VVM não precisa conhecer
                        print(f"WARNING: opcode {hex(opcode)} ({op_name}) not implemented in CoreService")
                    return
        print(f"ERROR: opcode {hex(opcode)} not found in CoreService")

    # -------------------------------
    # Arithmetic ops
    # -------------------------------
    def _exec_add(self, dest, src):
        if dest in self.variables:
            src_val = self._get_value(src)
            if isinstance(src_val, (int, float)):
                self.variables[dest] += src_val
        return self.variables.get(dest)

    def _exec_sub(self, dest, src):
        if dest in self.variables:
            src_val = self._get_value(src)
            if isinstance(src_val, (int, float)):
                self.variables[dest] -= src_val
        return self.variables.get(dest)

    def _exec_mul(self, dest, src):
        if dest in self.variables:
            src_val = self._get_value(src)
            if isinstance(src_val, (int, float)):
                self.variables[dest] *= src_val
        return self.variables.get(dest)

    def _exec_div(self, dest, src):
        if dest in self.variables:
            src_val = self._get_value(src)
            if isinstance(src_val, (int, float)):
                if src_val != 0:
                    self.variables[dest] /= src_val
                else:
                    self.variables[dest] = 0
        return self.variables.get(dest)

    def _exec_mod(self, dest, src):
        if dest in self.variables:
            src_val = self._get_value(src)
            if isinstance(src_val, (int, float)):
                if src_val != 0:
                    self.variables[dest] %= src_val
                else:
                    self.variables[dest] = 0
        return self.variables.get(dest)

    # -------------------------------
    # Logic ops
    # -------------------------------
    def _exec_eq(self, dest, a, b):
        if dest in self.variables:
            val_a = self._get_value(a)
            val_b = self._get_value(b)
            self.variables[dest] = 1 if val_a == val_b else 0
        return self.variables.get(dest)

    def _exec_neq(self, dest, a, b):
        if dest in self.variables:
            val_a = self._get_value(a)
            val_b = self._get_value(b)
            self.variables[dest] = 1 if val_a != val_b else 0
        return self.variables.get(dest)

    def _exec_gt(self, dest, a, b):
        if dest in self.variables:
            val_a = self._get_value(a)
            val_b = self._get_value(b)
            self.variables[dest] = 1 if val_a > val_b else 0
        return self.variables.get(dest)

    def _exec_lt(self, dest, a, b):
        if dest in self.variables:
            val_a = self._get_value(a)
            val_b = self._get_value(b)
            self.variables[dest] = 1 if val_a < val_b else 0
        return self.variables.get(dest)

    def _exec_gte(self, dest, a, b):
        if dest in self.variables:
            val_a = self._get_value(a)
            val_b = self._get_value(b)
            self.variables[dest] = 1 if val_a >= val_b else 0
        return self.variables.get(dest)

    def _exec_lte(self, dest, a, b):
        if dest in self.variables:
            val_a = self._get_value(a)
            val_b = self._get_value(b)
            self.variables[dest] = 1 if val_a <= val_b else 0
        return self.variables.get(dest)

    def _exec_and(self, dest, a, b):
        if dest in self.variables:
            val_a = self._get_value(a)
            val_b = self._get_value(b)
            self.variables[dest] = 1 if val_a and val_b else 0
        return self.variables.get(dest)

    def _exec_or(self, dest, a, b):
        if dest in self.variables:
            val_a = self._get_value(a)
            val_b = self._get_value(b)
            self.variables[dest] = 1 if val_a or val_b else 0
        return self.variables.get(dest)

    def _exec_not(self, dest, a):
        if dest in self.variables:
            val_a = self._get_value(a)
            self.variables[dest] = 1 if not val_a else 0
        return self.variables.get(dest)

    # -------------------------------
    # Data Structure ops
    # -------------------------------
    def _exec_array(self, var_name, size=0, default_value=0):
        self.variables[var_name] = [default_value] * size
        return self.variables.get(var_name)

    def _exec_push(self, var_name, value):
        if var_name in self.variables and isinstance(self.variables[var_name], list):
            self.variables[var_name].append(self._get_value(value))
        return self.variables.get(var_name)

    def _exec_pop(self, var_name):
        if var_name in self.variables and isinstance(self.variables[var_name], list):
            if self.variables[var_name]:
                return self.variables[var_name].pop()
        return None

    def _exec_get(self, var_name, index, dest_var=None):
        if var_name in self.variables and isinstance(self.variables[var_name], list):
            index_val = self._get_value(index)
            if 0 <= index_val < len(self.variables[var_name]):
                value = self.variables[var_name][index_val]
                if dest_var and dest_var in self.variables:
                    self.variables[dest_var] = value
                return value
        return None

    def _exec_set(self, var_name, index, value):
        if var_name in self.variables and isinstance(self.variables[var_name], list):
            index_val = self._get_value(index)
            value_val = self._get_value(value)
            if 0 <= index_val < len(self.variables[var_name]):
                self.variables[var_name][index_val] = value_val
        return self.variables.get(var_name)

    def _exec_length(self, var_name, dest_var=None):
        if var_name in self.variables and isinstance(self.variables[var_name], list):
            length = len(self.variables[var_name])
            if dest_var and dest_var in self.variables:
                self.variables[dest_var] = length
            return length
        return None

    # -------------------------------
    # Variables
    # -------------------------------
    def _exec_var_i(self, value=None):
        if value is not None: self.variables["var_i"] = value
        return self.variables["var_i"]

    def _exec_var_x(self, value=None):
        if value is not None: self.variables["var_x"] = value
        return self.variables["var_x"]

    def _exec_var_y(self, value=None):
        if value is not None: self.variables["var_y"] = value
        return self.variables["var_y"]

    def _exec_var_z(self, value=None):
        if value is not None: self.variables["var_z"] = value
        return self.variables["var_z"]

    def _exec_var_temp(self, value=None):
        if value is not None: self.variables["var_temp"] = value
        return self.variables["var_temp"]
    
    def _exec_var_mov(self, dest, src):
        if dest in self.variables and src in self.variables:
            self.variables[dest] = self.variables[src]
        return self.variables.get(dest)