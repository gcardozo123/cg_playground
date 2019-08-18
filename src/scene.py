from abc import abstractmethod


class Scene:
    @abstractmethod
    def update(self):
        pass