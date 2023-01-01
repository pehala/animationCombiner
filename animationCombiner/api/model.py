from dataclasses import dataclass
from functools import cached_property
from typing import Dict, List, Optional

from mathutils import Vector, Quaternion


@dataclass
class Bone:
    name: str
    pos: Vector
    children: List["Bone"]
    parent: Optional["Bone"] = None
    bone = None


@dataclass
class Pose:
    bones: Dict[str, Vector]
    relations: Dict[str, List[str]]

    @cached_property
    def root(self):
        root = Bone(name="root", pos=self.bones["root"], children=[])
        queue = [root]
        while len(queue) > 0:
            bone = queue.pop()
            if bone.name in self.relations:
                for child_key in self.relations[bone.name]:
                    child = Bone(name=child_key, pos=self.bones[child_key], children=[], parent=bone)
                    bone.children.append(child)
                    queue.append(child)
        return root


@dataclass
class Transition:
    bones: Dict[str, Quaternion]


@dataclass
class Animation:
    pose: Pose
    transitions: List[Transition]

    @property
    def length(self):
        return len(self.transitions)
