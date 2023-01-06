import re
from os import PathLike
from typing import Collection

from mathutils import Vector

from animationCombiner.parsers import AnimationLoader, AnimationExporter, register_parser, register_exporter
from animationCombiner.api.model import Pose, Animation, Transition


class MessifLoader(AnimationLoader):
    def scrub_file(self) -> int:
        return len(self.animations[0])

    # LINE = re.compile(r"")

    def __init__(self, names, relations, file, path) -> None:
        super().__init__(file, path)
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

    def load_skeletons(self) -> list[Pose]:
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


@register_parser(extensions={".data"})
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

    def __init__(self, file, path) -> None:
        super().__init__(self.NAMES, self.RELATIONS, file, path)


@register_exporter(extensions={".data"})
class HDM05MessifExporter(AnimationExporter):
    def export_animations(self, transitions: Collection[Transition], file):
        file.write("#objectKey messif.objects.keys.AbstractObjectKey 3361_31_757_198\n")
        file.write("1;mcdr.objects.ObjectMocapPose\n")
        for transition in transitions:
            data = []
            for name in HDM05MessifLoader.NAMES:
                data.append(transition.bones[name])
            file.write("; ".join(f"{vec[0]}, {vec[1]}, {vec[2]}" for vec in data) + "\n")
