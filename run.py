# run.py
from vvm import VVMInstance

def main():
    vexi_filepath = "sum.vexi"

    # --- Executar .vexi ---
    print(f"--- Running {vexi_filepath} with VVM ---")
    runtime_vm = VVMInstance()
    runtime_vm.run(vexi_filepath)

if __name__ == "__main__":
    main()