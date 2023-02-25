from functools import cached_property

from bpy.props import FloatVectorProperty, CollectionProperty, StringProperty
from bpy.types import PropertyGroup
from mathutils import Quaternion

from animationCombiner.api.model import RawAnimation, Pose
from animationCombiner.api.skeletons import Skeleton


class CoordsProperty(PropertyGroup):
    coords: FloatVectorProperty(size=3, precision=6, subtype="COORDINATES", unit="NONE")


class TranslationProperty(PropertyGroup):
    translation: FloatVectorProperty(size=3, precision=6, subtype="TRANSLATION", unit="NONE")


class RotationProperty(PropertyGroup):
    rotation: FloatVectorProperty(size=4, precision=6, subtype="QUATERNION", unit="ROTATION")


class Rotations(PropertyGroup):
    rotations: CollectionProperty(type=RotationProperty)


def calculate_rotation(diff: Quaternion, bone, first: Pose, current: Pose, skeleton: Skeleton, results: dict[str, Quaternion]):
    pos = first.bones[bone].copy()
    pos.rotate(diff)
    rotation = current.bones[bone].rotation_difference(pos)
    results[bone] = rotation
    diff = diff * rotation
    for child in skeleton.relations.get(bone, []):
        calculate_rotation(diff, child, first, current, skeleton, results)


class Animation(PropertyGroup):
    raw_order: StringProperty()

    skeleton: CollectionProperty(type=CoordsProperty)
    movement: CollectionProperty(type=TranslationProperty)
    animation: CollectionProperty(type=Rotations)

    def from_raw(self, raw_animation: RawAnimation, skeleton: Skeleton):
        self.raw_order = ",".join(skeleton.order())

        first_pose = raw_animation.poses[0]
        for bone in skeleton.order():
            pos = self.skeleton.add()
            pos.coords = first_pose.bones[bone]

        # TODO: Normalize

        # for pose in raw_animation.poses[1:]:
        #     anim = self.animation.add()
        #     for bone in skeleton.order():
        #         rotation = anim.rotations.add()
        #         rotation.rotation = pose.bones[bone].rotation_difference(first_pose.bones[bone])

        # Should fix rotation errors
        for pose in raw_animation.poses[1:]:
            anim = self.animation.add()
            results = {}
            calculate_rotation(Quaternion(), "root", first_pose, pose, skeleton, results)
            for bone in skeleton.order():
                rotation = anim.rotations.add()
                rotation.rotation = results[bone]

    def copy_from(self, other: "Animation"):
        self.raw_order = other.raw_order
        self.skeleton = other.skeleton
        self.movement = other.movement
        self.animation = other.animation

    @cached_property
    def order(self):
        return self.raw_order.split(",")

    @cached_property
    def length(self):
        return len(self.animation)
