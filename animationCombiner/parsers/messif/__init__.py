import re
from typing import Collection

from mathutils import Vector

from animationCombiner.api.loader import SkeletonLoader, AnimationLoader
from animationCombiner.api.model import Pose, Animation, Transition


class MessifLoader(SkeletonLoader, AnimationLoader):
    LINE = re.compile(r"")

    def __init__(self, names, relations, file) -> None:
        super().__init__()
        self.names = names
        self.relations = relations
        self.animations = self.parse(file)

    def parse(self, file):
        animations = []
        animation = []
        i = 0

        while line := file.readline():
            i += 1
            if line.startswith("#objectKey"):
                if len(animation) > 0:
                    animations.append(animation)
                animation = []
                # ignore type line
                file.readline()
                i += 1
            else:
                animation.append(self.parse_skeleton(line, i))
        if len(animation) > 0:
            animations.append(animation)
        return animations

    def load_skeletons(self) -> Collection[Pose]:
        return [animation[0] for animation in self.animations]

    def load_animations(self) -> Collection[Animation]:
        animations = []
        for animation in self.animations:
            pose = animation[0]
            transitions = []
            for p1 in animation[1:]:
                bones = {}
                for bone in pose.bones.keys():
                    bones[bone] = pose.bones[bone].rotation_difference(p1.bones[bone])
                transitions.append(Transition(bones))
            animations.append(Animation(pose, transitions.copy()))
        return animations

    def parse_skeleton(self, line, line_number):
        bones = {}
        vectors = line.split(";")
        assert len(vectors) == len(self.names), f"Incompatible skeleton at line {line_number}"
        for i, vector in enumerate(vectors):
            numbers = vector.split(",")
            assert len(numbers) == 3, f"Incorrect vector dimensions at line {line_number}"
            bones[self.names[i]] = Vector(tuple(float(number) for number in numbers))
        return Pose(bones=bones, relations=self.relations)


class HDM05MessifLoader(MessifLoader):
    NAMES = [
        "root",
        "lhipjoint",
        "lfemur",
        "ltibia",
        "lfoot",
        "ltoes",
        "rhipjoint",
        "rfemur",
        "rtibia",
        "rfoot",
        "rtoes",
        "lowerback",
        "upperback",
        "thorax",
        "lowerneck",
        "upperneck",
        "head",
        "lclavicle",
        "lhumerus",
        "lradius",
        "lwrist",
        "lhand",
        "lfingers",
        "lthumb",
        "rclavicle",
        "rhumerus",
        "rradius",
        "rwrist",
        "rhand",
        "rfingers",
        "rthumb",
    ]
    RELATIONS = {
        "root": ["lowerback", "lhipjoint", "rhipjoint"],
        "lowerback": ["upperback"],
        "upperback": ["thorax"],
        "thorax": ["lowerneck", "lclavicle", "rclavicle"],
        "lowerneck": ["upperneck"],
        "upperneck": ["head"],
        "lclavicle": ["lhumerus"],
        "lhumerus": ["lradius"],
        "lradius": ["lwrist"],
        "lwrist": ["lhand", "lthumb"],
        "lhand": ["lfingers"],
        "rclavicle": ["rhumerus"],
        "rhumerus": ["rradius"],
        "rradius": ["rwrist"],
        "rwrist": ["rhand", "rthumb"],
        "rhand": ["rfingers"],
        "lhipjoint": ["lfemur"],
        "lfemur": ["ltibia"],
        "ltibia": ["lfoot"],
        "lfoot": ["ltoes"],
        "rhipjoint": ["rfemur"],
        "rfemur": ["rtibia"],
        "rtibia": ["rfoot"],
        "rfoot": ["rtoes"],
    }

    def __init__(self, file) -> None:
        super().__init__(self.NAMES, self.RELATIONS, file)
