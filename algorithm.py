class GGTAlgorithm:
    def __init__(self, initial_value: int):
        self.M = initial_value
        self.last_M = None

    def update_value(self, incoming_value: int) -> bool:
        if incoming_value < self.M:
            self.last_M = self.M
            self.M = (self.M - 1) % incoming_value + 1
            return True
        return False
