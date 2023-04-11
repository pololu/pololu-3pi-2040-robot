class Encoders:
    def __init__(self):
        from ._lib.pio_quadrature_counter import PIOQuadratureCounter
        self.left = PIOQuadratureCounter(0, 12, 13)
        self.right = PIOQuadratureCounter(1, 8, 9)
        self._flip_sign = 1

        # Zero counts
        self.left_offset = 0
        self.right_offset = 0
        self.get_counts(reset = True)

    def flip(self, flip):
        self._flip_sign = -1 if flip else 1

    def get_counts(self, reset = False):
        # Sign on the 3pi encoders is reversed from what
        # the PIO counter gives us.
        left = - self.left.read() - self.left_offset
        right = - self.right.read() - self.right_offset

        if reset:
            self.left_offset += left
            self.right_offset += right

        return [left * self._flip_sign, right * self._flip_sign]
