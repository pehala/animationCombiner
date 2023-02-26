from dataclasses import dataclass
from typing import Dict, List

from mathutils import Vector

from animationCombiner.api.skeletons import Skeleton


@dataclass
class Pose:
    """Positions of all bones in a specific frame"""

    bones: Dict[str, Vector]


@dataclass
class RawAnimation:
    """List of Poses of a specific skeleton"""

    poses: List[Pose]
    skeleton: Skeleton

    @property
    def length(self):
        return len(self.poses)
