
class CostError(Exception):

    def __init__(self, expresion, mensage):
        self.expresion = expresion
        self.mensage = mensage
