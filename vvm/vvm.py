# vvm/vvm.py
import lmdb
from core.tools import TOOLS  # Core codebook
from core.service import CoreService

class VVMInstance:
    def __init__(self, db_path="./vvm_db", map_size=10_485_760):
        """
        VVMInstance: Virtual Machine para executar bytecode.
        Args:
            db_path: caminho do LMDB
            map_size: tamanho máximo do DB (10MB por default)
        """
        # Cria o ambiente LMDB
        self.env = lmdb.open(db_path, map_size=map_size)
        
        # Inicializa o banco com o codebook
        self._init_codebook()
        self.core = CoreService()

        # Variáveis da VM
        self.variables = self.core.variables
        self.stack = []

        # Estado de gravação para compilação .vexi
        self.is_recording = False
        self.recorded_commands = []

    def _init_codebook(self):
        """Insere o core codebook no LMDB"""
        with self.env.begin(write=True) as txn:
            for group_name, group in TOOLS.items():
                for opcode, value in group.items():
                    key = opcode.to_bytes(2, "big")
                    # Armazena int como bytes, string como UTF-8
                    if isinstance(value, int):
                        val_bytes = value.to_bytes(4, "big")  # 4 bytes para int
                    else:
                        val_bytes = str(value).encode("utf-8")
                    txn.put(key, val_bytes)

    def exec_patch(self, patch):
        return self.core.exec_patch(patch)

    # -------------------------------
    # VEXI Compilation and Runtime
    # -------------------------------
    def start_recording(self):
        """Ativa o modo de gravação para capturar comandos."""
        self.is_recording = True
        self.recorded_commands = []

    def stop_and_save_vexi(self, filepath):
        """Para a gravação e salva os comandos em um arquivo .vexi."""
        self.is_recording = False
        try:
            with open(filepath, 'w') as f:
                f.write('\n'.join(self.recorded_commands))
            print(f"Successfully compiled to {filepath}")
        except IOError as e:
            print(f"Error saving file {filepath}: {e}")

    def run_vexi(self, filepath):
        """Carrega e executa um arquivo .vexi em formato de bytecode."""
        # --- 1. Parse Pass ---
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: File not found at {filepath}")
            return

        commands = []
        labels = {}
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('//'):
                commands.append(None)
                continue
            
            parts = [p.strip() for p in line.split(',')]
            
            # Check for LABEL pseudo-op first
            if parts[0] == 'LABEL':
                labels[parts[1]] = i
                commands.append(None)
            else:
                commands.append(parts)

        # --- 2. Execution Pass ---
        pc = 0
        while pc < len(commands):
            parts = commands[pc]
            if parts is None:
                pc += 1
                continue

            command_or_opcode = parts[0]
            args = []
            # Parse args, converting to numbers where possible
            for arg in parts[1:]:
                try:
                    args.append(int(arg) if arg.replace('-', '', 1).isdigit() else float(arg))
                except (ValueError, TypeError):
                    args.append(arg)
            
            jumped = False
            
            try:
                # Try to interpret as a core bytecode instruction
                opcode = int(command_or_opcode)
                # exec_patch expects a tuple of (opcode, single_arg_or_tuple_of_args)
                patch_args = tuple(args) if len(args) > 1 else (args[0] if args else None)
                self.core.exec_patch((opcode, patch_args))

            except ValueError:
                # If it's not an integer, treat as a pseudo-operation
                cmd_name = command_or_opcode
                if cmd_name == 'PRINT_STR':
                    print(args[0], end='')
                elif cmd_name == 'PRINT_VAR':
                    print(self.variables.get(args[0], f"Variable {args[0]} not found"))
                elif cmd_name == 'INPUT_INT':
                    self.variables[args[0]] = int(input())
                elif cmd_name == 'JMP':
                    pc = labels.get(args[0], pc + 1)
                    jumped = True
                elif cmd_name == 'JMP_IF_EQ':
                    var, val, label = args
                    if self._get_value(var) == self._get_value(val):
                        pc = labels.get(label, pc + 1)
                        jumped = True
                elif cmd_name == 'JMP_IF_NEQ':
                    var, val, label = args
                    if self._get_value(var) != self._get_value(val):
                        pc = labels.get(label, pc + 1)
                        jumped = True
                else:
                    print(f"WARNING: Pseudo-command '{cmd_name}' not recognized.")

            if not jumped:
                pc += 1
                
    def _get_value(self, operand):
        # Helper para obter o valor de uma variável ou usar um literal
        if isinstance(operand, str) and operand in self.variables:
            return self.variables[operand]
        return operand

    def _record_command(self, command, *args):
        if self.is_recording:
            # Converte todos os args para string para salvar no arquivo
            args_str = ','.join(map(str, args))
            self.recorded_commands.append(f"{command},{args_str}")

    # -------------------------------
    # High-level Assembly-like API
    # -------------------------------
    def _get_opcode(self, op_name):
        # Cache for reverse map could be created at init
        if not hasattr(self, '_opcode_reverse_map'):
            self._opcode_reverse_map = {}
            # Only iterate over groups that map opcodes to string names
            string_op_groups = [
                'arithmetic', 'logic', 'variables', 'control', 
                'data_structures', 'ds_operations', 'io', 'control_flow'
            ]
            for group_name in string_op_groups:
                group = TOOLS.get(group_name, {})
                for opcode, name in group.items():
                    if name not in self._opcode_reverse_map:
                        self._opcode_reverse_map[name] = opcode
        return self._opcode_reverse_map.get(op_name)

    def set(self, var_name, value):
        self._record_command('SET', var_name, value)
        self.core.variables[var_name] = self._get_value(value)

    def array(self, var_name, size, default_value=0):
        self._record_command('ARRAY', var_name, size, default_value)
        return self.exec_patch((self._get_opcode('ARRAY'), (var_name, size, default_value)))
    
    def aset(self, array_name, index, value):
        self._record_command('ASET', array_name, index, value)
        # Note: 'SET' is the name for the DS_OPERATION opcode 0x63
        return self.exec_patch((self._get_opcode('SET'), (array_name, self._get_value(index), self._get_value(value))))

    def mov(self, dest, src):
        self._record_command('MOV', dest, src)
        return self.exec_patch((self._get_opcode('var_mov'), (dest, src)))

    def add(self, dest, src):
        self._record_command('ADD', dest, src)
        return self.exec_patch((self._get_opcode('ADD'), (dest, self._get_value(src))))

    def sub(self, dest, src):
        self._record_command('SUB', dest, src)
        return self.exec_patch((self._get_opcode('SUB'), (dest, self._get_value(src))))

    def mul(self, dest, src):
        self._record_command('MUL', dest, src)
        return self.exec_patch((self._get_opcode('MUL'), (dest, self._get_value(src))))

    def div(self, dest, src):
        self._record_command('DIV', dest, src)
        return self.exec_patch((self._get_opcode('DIV'), (dest, self._get_value(src))))

    def mod(self, dest, src):
        self._record_command('MOD', dest, src)
        return self.exec_patch((self._get_opcode('MOD'), (dest, self._get_value(src))))

    # --- Logic Ops ---
    def get(self, array_name, index, dest_var):
        self._record_command('GET', array_name, index, dest_var)
        return self.exec_patch((self._get_opcode('GET'), (array_name, self._get_value(index), dest_var)))

    def eq(self, dest, a, b):
        self._record_command('EQ', dest, a, b)
        return self.exec_patch((self._get_opcode('EQ'), (dest, self._get_value(a), self._get_value(b))))

    def neq(self, dest, a, b):
        self._record_command('NEQ', dest, a, b)
        return self.exec_patch((self._get_opcode('NEQ'), (dest, self._get_value(a), self._get_value(b))))

    def and_op(self, dest, a, b):
        self._record_command('AND', dest, a, b)
        return self.exec_patch((self._get_opcode('AND'), (dest, self._get_value(a), self._get_value(b))))
        
    def or_op(self, dest, a, b):
        self._record_command('OR', dest, a, b)
        return self.exec_patch((self._get_opcode('OR'), (dest, self._get_value(a), self._get_value(b))))

    def not_op(self, dest, a):
        self._record_command('NOT', dest, a)
        return self.exec_patch((self._get_opcode('NOT'), (dest, self._get_value(a))))
