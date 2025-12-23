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

