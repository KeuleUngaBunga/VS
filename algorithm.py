class GGTAlgorithm:
    """GGT-Algorithmus (Größter Gemeinsamer Teiler)"""
    
    def __init__(self, initial_value: int):
        self.M = initial_value
        self.last_M = None

    def update_value(self, incoming_value: int) -> bool:
        """
        Aktualisiere M basierend auf eingehendem Wert.
        Gibt True zurück, wenn M sich geändert hat.
        """
        if incoming_value < self.M:
            self.last_M = self.M
            self.M = (self.M - 1) % incoming_value + 1
            return True
        return False
