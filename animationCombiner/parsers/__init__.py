import functools
from abc import ABC, abstractmethod
from functools import partial
from os import PathLike
from pathlib import Path
from typing import Collection, Type

from animationCombiner.api.model import Animation


class AnimationLoader(ABC):
    """Interface for importing Animations"""
    def __init__(self, file, path) -> None:
        self.path = path

    @abstractmethod
    def scrub_file(self) -> int:
        """
        Should verify that the file is valid and return number of animations present,
        in ideal world, it should be faster than load_animations, because the actual animations will be processed later again.
        """

    def load_animation(self) -> Animation:
        """Loads & returns iterable of transition to achieve the animation"""
        return next(iter(self.load_animations()))

    @abstractmethod
    def load_animations(self) -> Collection[Animation]:
        """Loads & returns initial Skeleton structure"""


class AnimationExporter(ABC):
    """Interface for exporting Animations"""
    @abstractmethod
    def export_animations(self, animations: Collection[Animation], file):
        """Writes animations to a file"""


PARSERS = {}
EXPORTERS = {}


class ParserError(Exception):
    """Error which indicates that something went wrong while parsing file"""
    def __init__(self, message, *args: object) -> None:
        self.message = message
        super().__init__(message, *args)


def _register_parser(func=None, *, extensions: Collection[str] = None, collection, clazz: Type):
    """Registers parser for specific extensions"""
    if not func:
        # The only drawback is that for functions there is no thing
        # like "self" - we have to rely on the decorator
        # function name on the module namespace
        return partial(_register_parser, extensions=extensions, collection=collection, clazz=clazz)
    if not issubclass(func, clazz):
        raise ValueError(f"Parsers need to be descendants of {clazz.__name__}")
    for extension in extensions:
        if extension in collection:
            raise ValueError(f"Class {func.__name__} cannot register extension {extension} because it is already "
                             f"registered by {collection[extension].__name__}")

        collection[extension] = func

    return func


def _find_parser_for_path(path: PathLike, collection):
    """Return descendant of AnimationLoader that is registered for that path"""
    path = Path(path)
    extension = path.suffix
    if extension not in collection:
        raise ParserError(f"Extension {extension} is not recognized")
    return collection[extension]


register_parser = functools.partial(_register_parser, collection=PARSERS, clazz=AnimationLoader)
register_exporter = functools.partial(_register_parser, collection=EXPORTERS, clazz=AnimationExporter)


def find_parser_for_path(path: PathLike) -> Type["AnimationLoader"]:
    """Return descendant of AnimationLoader that is registered for that path"""
    path = Path(path)
    if not path.exists() or not path.is_file():
        raise ParserError(f"Path {path} must exists and must be a file")
    return _find_parser_for_path(path, PARSERS)


def find_exporter_for_path(path: PathLike) -> Type["AnimationExporter"]:
    """Return descendant of AnimationLoader that is registered for that path"""
    return _find_parser_for_path(path, EXPORTERS)


def load_animation_from_path(path: PathLike) -> Animation:
    with open(path, "r") as file:
        return find_parser_for_path(path)(file, path).load_animation()


