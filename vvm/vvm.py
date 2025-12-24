import lmdb
from core.service import CoreService

class VVMInstance:
    def __init__(self):
        self.core = CoreService()

    def run(self, program):
        pc = 0
        while pc < len(program):
            opcode, args = program[pc]
            pc = self.core.exec(opcode, args, pc)
