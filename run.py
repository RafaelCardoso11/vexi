# run.py
from vvm import VVMInstance

def parse_vexi(filepath):
    program = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(',')]
            opcode = int(parts[0], 16)
            args = tuple(int(p, 16) for p in parts[1:])
            program.append((opcode, args))
    return program

def main():
    vexi_filepath = "sum.vexi"
    program = parse_vexi(vexi_filepath)

    # --- Executar .vexi ---
    print(f"--- Running {vexi_filepath} with VVM ---")
    runtime_vm = VVMInstance()
    runtime_vm.run(program)

if __name__ == "__main__":
    main()