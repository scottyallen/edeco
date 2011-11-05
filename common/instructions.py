import operations


class GenericInstruction:
    def __init__(self, address, mnemonic, operands):
        self.addr = address
        self.address = self.addrtoint()
        self.mnemonic = mnemonic
        self.operands = operands

        # a little bridge to make an Instruction closer to a small Operation
        self.operation_result = None

        # get rid of these eventually. replacement will be handled in a structured manner
        self.used_in = [] # list of addresses of final instructions this one contributed to
        self.replaced_by = None # an Operation that completely replaces this instruction

    def addrtoint(self):
        return int(self.addr, 16)

    def mark_chain(self, address):
        self.used_in.append(address)

    def __str__(self):
        ins = ' '.join([self.addr + ':   ', self.mnemonic] + self.operands)
        if self.used_in:
            ins = ins + ' // ' + ' '.join(self.used_in)
        if self.replaced_by is not None:
            ins = '// ' + ins + '\n' + str(self.replaced_by) + '\n'
        return ins

    def evaluate(self, machine_state):
        """Changes the machine state to the best of out knowledge. no return value.
        """
        raise NotImplementedError

    def get_read_regs(self):
        state = operations.DummyMachineState()
        self.evaluate(state)
        return state.get_read_places()

    def get_modified_regs(self):
        state = operations.DummyMachineState()
        self.evaluate(state)
        return state.get_written_places()

    def get_value(self, context, reg_spec):
        instructions, index, memory = context
        state = operations.MachineState(memory)
        for reg in self.get_read_regs():
            value = operations.traceback_register(context, reg)
            try:
                state.regs.set(reg, value)
            except:
                raise NotImplementedError
        self.evaluate(state)
        return state.regs.get(reg_spec)


def Instruction(address, mnemonic, operands, instruction_map):
    """Creates instructions based on instruction_map"""
    try:
        cls = instruction_map[mnemonic]
    except KeyError:
        cls = GenericInstruction
    try:
        return cls(address, mnemonic, operands)
    except:
        print GenericInstruction(address, mnemonic, operands)
        raise