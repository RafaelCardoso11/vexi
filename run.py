# run.py
from vvm import VVMInstance

def main():
    vexi_filepath = "complex_arithmetic.vexi"

    # --- Executar .vexi ---
    print(f"--- Running {vexi_filepath} with VVM ---")
    runtime_vm = VVMInstance()
    runtime_vm.run_vexi(vexi_filepath)
    print("--- Execution Finished ---\n")

    # --- Verificação ---
    print("--- Verification ---")
    print(f"var_x expected: 5, got: {runtime_vm.variables['var_x']}")
    print(f"var_y expected: 1, got: {runtime_vm.variables['var_y']}")
    print(f"var_z expected: 10, got: {runtime_vm.variables['var_z']}")
    print("-" * 20)


if __name__ == "__main__":
    main()