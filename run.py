# run.py
from vvm import VVMInstance

def main():
    vexi_filepath = "sum_to_n.vexi"

    # --- Executar .vexi ---
    print(f"--- Running {vexi_filepath} with VVM ---")
    runtime_vm = VVMInstance()
    runtime_vm.run_vexi(vexi_filepath)

if __name__ == "__main__":
    main()