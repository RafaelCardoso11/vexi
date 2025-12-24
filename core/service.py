from .tools import TOOLS

class CoreService:
    def __init__(self):
        # Variáveis nomeadas (mantém compatibilidade atual)
        self.variables = dict.fromkeys(TOOLS["variables"].values(), 0)
        self.stack = []

    # -------------------------------
    # Helpers
    # -------------------------------
    def _get_value(self, operand):
        if isinstance(operand, str) and operand in self.variables:
            return self.variables[operand]
        return operand

    # -------------------------------
    # Constants handling (multi-byte)
    # -------------------------------
    def get_constant(self, *codes):
        value = 0
        for c in codes:
            value = (value << 8) + TOOLS["constants"].get(c, c)
        return value

    # -------------------------------
    # Execute instruction
    # Retorna o próximo PC
    # -------------------------------
    def exec(self, opcode, args, pc):
        for group_name, group in TOOLS.items():
            if opcode in group:
                op_name = group[opcode]

                # Handle direct variable setting
                if group_name == "variables":
                    self.variables[op_name] = self._get_value(args[0])
                    return pc + 1

                method = getattr(self, f"_exec_{op_name.lower()}", None)
                if not method:
                    raise RuntimeError(f"Opcode {hex(opcode)} ({op_name}) not implemented")

                if args is None:
                    args = ()
                elif not isinstance(args, (list, tuple)):
                    args = (args,)
                
                # Map variable codes to names
                mapped_args = []
                for arg in args:
                    if arg in TOOLS["variables"]:
                        mapped_args.append(TOOLS["variables"][arg])
                    else:
                        mapped_args.append(arg)

                result = method(*mapped_args)

                # controle de fluxo: se retornar int → novo pc
                if isinstance(result, int) and op_name.startswith("JMP"):
                    return result

                return pc + 1

        raise RuntimeError(f"Opcode {hex(opcode)} not found")

    # -------------------------------
    # Arithmetic ops
    # -------------------------------
    def _exec_add(self, dest, src):
        self.variables[dest] += self._get_value(src)

    def _exec_sub(self, dest, src):
        self.variables[dest] -= self._get_value(src)

    def _exec_mul(self, dest, src):
        self.variables[dest] *= self._get_value(src)

    def _exec_div(self, dest, src):
        v = self._get_value(src)
        self.variables[dest] = self.variables[dest] / v if v != 0 else 0

    def _exec_mod(self, dest, src):
        v = self._get_value(src)
        self.variables[dest] = self.variables[dest] % v if v != 0 else 0

    # -------------------------------
    # Logic ops
    # -------------------------------
    def _exec_eq(self, dest, a, b):
        self.variables[dest] = 1 if self._get_value(a) == self._get_value(b) else 0

    def _exec_neq(self, dest, a, b):
        self.variables[dest] = 1 if self._get_value(a) != self._get_value(b) else 0

    def _exec_gt(self, dest, a, b):
        self.variables[dest] = 1 if self._get_value(a) > self._get_value(b) else 0

    def _exec_lt(self, dest, a, b):
        self.variables[dest] = 1 if self._get_value(a) < self._get_value(b) else 0

    def _exec_gte(self, dest, a, b):
        self.variables[dest] = 1 if self._get_value(a) >= self._get_value(b) else 0

    def _exec_lte(self, dest, a, b):
        self.variables[dest] = 1 if self._get_value(a) <= self._get_value(b) else 0

    def _exec_and(self, dest, a, b):
        self.variables[dest] = 1 if self._get_value(a) and self._get_value(b) else 0

    def _exec_or(self, dest, a, b):
        self.variables[dest] = 1 if self._get_value(a) or self._get_value(b) else 0

    def _exec_not(self, dest, a):
        self.variables[dest] = 0 if self._get_value(a) else 1

    # -------------------------------
    # Control Flow (CORE, não VM)
    # -------------------------------
    def _exec_jmp(self, target_pc):
        return target_pc

    def _exec_jmp_if_eq(self, a, b, target_pc):
        if self._get_value(a) == self._get_value(b):
            return target_pc

    def _exec_jmp_if_neq(self, a, b, target_pc):
        if self._get_value(a) != self._get_value(b):
            return target_pc

    # -------------------------------
    # Data Structures
    # -------------------------------
    def _exec_array(self, var_name, size, default=0):
        self.variables[var_name] = [default] * size

    def _exec_push(self, var_name, value):
        self.variables[var_name].append(self._get_value(value))

    def _exec_pop(self, var_name):
        return self.variables[var_name].pop()

    def _exec_get(self, arr, index, dest):
        self.variables[dest] = self.variables[arr][self._get_value(index)]

    def _exec_set(self, arr, index, value):
        self.variables[arr][self._get_value(index)] = self._get_value(value)

    def _exec_length(self, arr, dest):
        self.variables[dest] = len(self.variables[arr])

    # -------------------------------
    # Variables
    # -------------------------------
    def _exec_var_mov(self, dest, src):
        self.variables[dest] = self.variables[src]