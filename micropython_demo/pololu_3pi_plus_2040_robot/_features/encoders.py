from .._lib.pio_quadrature_counter import PIOQuadratureCounter

class Encoders:
    def __init__(self):
        self.left = PIOQuadratureCounter(0, 12, 13)
        self.right = PIOQuadratureCounter(1, 8, 9)

    def get_counts(self):
        # Sign on the 3pi encoders is reversed from what
        # the PIO counter gives us.
        return [-self.left.read(), -self.right.read()]
        
