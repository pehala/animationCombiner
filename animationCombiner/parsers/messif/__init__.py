from typing import Collection

import numpy
import numpy as np
from mathutils import Vector

from animationCombiner.parsers import (
    AnimationLoader,
    AnimationExporter,
    register_parser,
    register_exporter,
)
from animationCombiner.api.skeletons import HDMSkeleton
from animationCombiner.api.model import Pose, RawAnimation


class MessifLoader(AnimationLoader):
    def scrub_file(self) -> int:
        return len(self.animations[0])

    def __init__(self, bone_order, skeleton, file, path) -> None:
        super().__init__(file, path)
        self.bone_order = bone_order
        self.skeleton = skeleton
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

    def load_animations(self) -> Collection[RawAnimation]:
        animations = []
        for animation in self.animations:
            # pose = animation[0]
            # poses = []
            # for p1 in animation[1:]:
            #     bones = {}
            #     for bone in pose.bones.keys():
            #         bones[bone] = pose.bones[bone].rotation_difference(p1.bones[bone])
            #     poses.append(Pose(bones))
            animations.append(RawAnimation(animation, self.skeleton))
        return animations

    def parse_skeleton(self, line, line_number):
        bones = {}
        vectors = line.split(";")
        assert len(vectors) == len(self.bone_order), f"Incompatible skeleton at line {line_number}"
        for i, vector in enumerate(vectors):
            numbers = vector.split(",")
            assert len(numbers) == 3, f"Incorrect vector dimensions at line {line_number}"
            bones[self.bone_order[i]] = Vector(np.asarray(numbers, dtype=numpy.double))
        return Pose(bones=bones)


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

    def __init__(self, file, path) -> None:
        super().__init__(self.NAMES, HDMSkeleton(), file, path)


@register_exporter(extensions={".data"})
class HDM05MessifExporter(AnimationExporter):
    def export_animation(self, animation: RawAnimation, file):
        file.write("#objectKey messif.objects.keys.AbstractObjectKey 3361_31_757_198\n")
        file.write("1;mcdr.objects.ObjectMocapPose\n")
        for pose in animation.poses:
            data = []
            for name in HDM05MessifLoader.NAMES:
                data.append(pose.bones[name])
            file.write("; ".join(f"{vec[0]}, {vec[1]}, {vec[2]}" for vec in data) + "\n")
