from abc import ABC, abstractmethod


class AbstractRepository(ABC):
    """Repository abstract class

    Repositories are interfaces and act as a middleman between the ORM and the
    user, allowing to encapsulate all object manipulation logic.

    Idea is to be agnostic in case changes of technology directions happens in
    the future.

    Coupled with services for maximum decoupling and testing capabilities.

    It's also easier to mock in tests.

    Extend this class to impact all repositories.

    Left unimplemented but as example for context / evolution.

    Source & ideas: https://www.cosmicpython.com/book/preface.html
    """

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def create(*args, **kwargs) -> object:
        """Adds one object to the database"""
        raise NotImplementedError

    @abstractmethod
    def bulk_create(self, *args, **kwargs) -> list[object]:
        """Adds a list of objects to the database"""
        raise NotImplementedError

    @abstractmethod
    def retrieve(self, *args, **kwargs) -> object | list[object]:
        """Returns a specific object or a list of objects"""
        raise NotImplementedError

    @abstractmethod
    def update(self, *args, **kwargs) -> object:
        """Updates an object in the database & returns the updated object"""
        raise NotImplementedError

    @abstractmethod
    def delete(self, *args, **kwargs) -> object:
        """Deletes an object in the database & returns the deleted object"""
        raise NotImplementedError
