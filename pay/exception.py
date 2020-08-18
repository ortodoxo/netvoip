class CostError(Exception):
    def __init__(self, expresion, mensage):
        self.expresion = expresion
        self.mensage = mensage

class SupplierError(Exception):
    def __init__(self, expresion, mensage):
        self.expresion = expresion
        self.mensage = mensage

class BalanceError(Exception):
    def __init__(self,expresion, mensage):
        self.expresion  = expresion
        self.mensage = mensage

class CdrExportError(Exception):
    def __init__(self,expresion, mensage):
        self.expresion = expresion
        self.mensage = mensage
