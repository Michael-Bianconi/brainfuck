class Instruction:

    def __init__(self, operation: callable, allowed_operands: list):
        self.allowed_operations = allowed_operands
        self.operation = operation

    def operands_match(self, operands):
        for allowed_operands in self.allowed_operations:
            matched = False
            if len(operands) == len(allowed_operands):
                matched = True
                for i in range(len(operands)):
                    if not isinstance(operands[i], allowed_operands[i]):
                        matched = False
                        break
            if matched:
                return allowed_operands
        return None