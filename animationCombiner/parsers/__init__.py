import os
from abc import ABC, abstractmethod
from functools import wraps, partial
from os import PathLike
from pathlib import Path
from typing import Collection, Type

from animationCombiner.api.model import Animation

PARSERS = {}


class ParserError(Exception):
    """Error which indicates that something went wrong while parsing file"""
    def __init__(self, message, *args: object) -> None:
        self.message = message
        super().__init__(message, *args)


def register_parser(func=None, *, extensions: Collection[str] = None):
    """Registers parser for specific extensions"""
    if not func:
        # The only drawback is that for functions there is no thing
        # like "self" - we have to rely on the decorator
        # function name on the module namespace
        return partial(register_parser, extensions=extensions)
    if not issubclass(func, AnimationLoader):
        raise ValueError("Parsers need to be descendants of AnimationLoader")
    for extension in extensions:
        if extension in PARSERS:
            raise ValueError(f"Class {func.__name__} cannot register extension {extension} because it is already "
                             f"registered by {PARSERS[extension].__name__}")

        PARSERS[extension] = func

    return func


def find_parser_for_path(path: PathLike) -> Type["AnimationLoader"]:
    """Return descendant of AnimationLoader that is registered for that path"""
    path = Path(path)
    if not path.exists() or not path.is_file():
        raise ParserError(f"Path {path} must exists and must be a file")
    extension = path.suffix
    if extension not in PARSERS:
        raise ParserError(f"Extension {extension} is not recognized")
    return PARSERS[extension]


# class FileLoader(ABC):
#
#     # pylint: disable=unused-argument
#     def __init__(self, file, path) -> None:
#         self.path = path
#
#     def scrub
    # @staticmethod
    # def require_file(path: PathLike) -> bool:
    #     """Return true, if the path exists and is a file"""
    #     return os.path.exists(path) and os.path.isfile(path)
    #
    # def require_extensions(self, path: PathLike, extensions: Collection[str]) -> bool:
    #     """Return true, if the files extension is in extensions"""
    #     return self.require_file(path) and Path(path).suffix in extensions
    #
    # @abstractmethod
    # def fits(self, path: PathLike) -> bool:
    #     """Return True, if the path can be parsed by this parser"""


# class SkeletonLoader(FileLoader):
#     def load_skeleton(self) -> Pose:
#         """Loads & returns initial Skeleton structure"""
#         return next(iter(self.load_skeletons()))
#
#     @abstractmethod
#     def load_skeletons(self) -> Collection[Pose]:
#         """Loads & returns initial Skeleton structure"""


class AnimationLoader(ABC):
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
