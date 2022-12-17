from abc import ABC, abstractmethod
from typing import Collection

from .model import Pose, Animation


class SkeletonLoader(ABC):
    def load_skeleton(self) -> Pose:
        """Loads & returns initial Skeleton structure"""
        return next(iter(self.load_skeletons()))

    @abstractmethod
    def load_skeletons(self) -> Collection[Pose]:
        """Loads & returns initial Skeleton structure"""


class AnimationLoader(ABC):
    def load_animation(self) -> Animation:
        """Loads & returns iterable of transition to achieve the animation"""
        return next(iter(self.load_animations()))

    @abstractmethod
    def load_animations(self) -> Collection[Animation]:
        """Loads & returns initial Skeleton structure"""
