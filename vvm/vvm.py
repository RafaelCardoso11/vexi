import lmdb
from core.tools import TOOLS
from core.service import CoreService

class VVMInstance:
    def __init__(self, db_path="./vvm_db", map_size=10_485_760):
        self.env = lmdb.open(db_path, map_size=map_size)
        self._init_codebook()
        self.core = CoreService()
        self.variables = self.core.variables

    def _init_codebook(self):
        with self.env.begin(write=True) as txn:
            for group_name, group in TOOLS.items():
                for opcode, value in group.items():
                    key = opcode.to_bytes(2, "big")
                    if isinstance(value, int):
                        val_bytes = value.to_bytes(4, "big")
                    else:
                        val_bytes = str(value).encode("utf-8")
                    txn.put(key, val_bytes)

    def run_vexi(self, filepath):
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: File not found at {filepath}")
            return

        program = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = [p.strip() for p in line.split(',')]
            
            command_opcode = parts[0]
            args = []
            
            try:
                if command_opcode.startswith('0x'):
                    opcode = int(command_opcode, 16)
                else:
                    opcode = int(command_opcode)
            except ValueError:
                print(f"Error: Invalid opcode format '{command_opcode}'. Must be integer or hex (e.g., 0xNN).")
                return

            for arg in parts[1:]:
                try:
                    if arg.startswith('0x'):
                        args.append(int(arg, 16))
                    else:
                        args.append(int(arg))
                except (ValueError, TypeError):
                    args.append(arg)

            program.append((opcode, tuple(args)))

        pc = 0
        while pc < len(program):
            opcode, args = program[pc]
            pc = self.core.exec(opcode, args, pc)
