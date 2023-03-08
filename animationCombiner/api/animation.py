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


def calculate_rotation(
    parent,
    bone,
    first_pose: Pose,
    current_pose: Pose,
    skeleton: Skeleton,
    results: dict[str, Quaternion],
):
    if parent:
        first = first_pose.bones[bone] - first_pose.bones[parent]
        current = current_pose.bones[bone] - current_pose.bones[parent]
    else:
        first = first_pose.bones[bone]
        current = current_pose.bones[bone]
    rotation = first.rotation_difference(current)
    results[bone] = rotation
    for child in skeleton.relations.get(bone, []):
        calculate_rotation(bone, child, first_pose, current_pose, skeleton, results)


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

        # Should fix rotation errors
        for pose in raw_animation.poses[1:]:
            anim = self.animation.add()
            results = {}
            calculate_rotation(None, "root", first_pose, pose, skeleton, results)
            for bone in skeleton.order():
                rotation = anim.rotations.add()
                rotation.rotation = results[bone]

    @cached_property
    def order(self):
        return self.raw_order.split(",")

    @cached_property
    def length(self):
        return len(self.animation)
