from abc import ABC, abstractmethod


class Animal(ABC):
    @abstractmethod
    def make_sound(self):
        pass

    def describe(self):
        return "This is an animal."


class Dog(Animal):
    def make_sound(self):
        return "Woof"


class Cat(Animal):
    def make_sound(self):
        return "Meow"


class Cow(Animal):
    def make_sound(self):
        return "Moo"


if __name__ == "__main__":
    animals = [Dog(), Cat(), Cow()]
    for animal in animals:
        print(animal.make_sound(), "|", animal.describe())
