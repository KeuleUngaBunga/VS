from abc import ABC, abstractmethod


class Datastore(ABC):
    @abstractmethod
    def write(self, index: int, data: str) -> None:
        pass

    @abstractmethod
    def read(self, index: int) -> str:
        pass


class DatastoreImpl(Datastore):

    def __init__(self):
        self.store = {}

    def write(self, index: int, data: str) -> None:
        if not isinstance(index, int) or index < 0:
            raise ValueError("Index cannot be negative and has to be integer")
        if not isinstance(data, str):
            raise ValueError("Data must be a string")
        self.store[index] = data
        print(f"Data written at index {index}: {data}")

    def read(self, index: int) -> str:
        if not isinstance(index, int) or index < 0:
            raise ValueError("Index cannot be negative and has to be integer")
        if index not in self.store:
            raise IndexError(f"No element at index {index}")
        return self.store[index]
