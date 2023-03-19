from functools import cached_property

from bpy.props import FloatVectorProperty, CollectionProperty, StringProperty
from bpy.types import PropertyGroup

from animationCombiner.api.model import RawAnimation, Pose
from animationCombiner.api.skeletons import Skeleton
from animationCombiner.utils.rotation import calculate_frames


class CoordsProperty(PropertyGroup):
    coords: FloatVectorProperty(size=3, precision=6, subtype="COORDINATES", unit="NONE")


class TranslationProperty(PropertyGroup):
    translation: FloatVectorProperty(size=3, precision=6, subtype="TRANSLATION", unit="NONE")


class RotationProperty(PropertyGroup):
    rotation: FloatVectorProperty(size=4, precision=6, subtype="QUATERNION", unit="ROTATION")


class Rotations(PropertyGroup):
    rotations: CollectionProperty(type=RotationProperty)


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
        for frame in calculate_frames(raw_animation):
            anim = self.animation.add()
            for bone in skeleton.order():
                rotation = anim.rotations.add()
                rotation.rotation = frame[bone]

    @cached_property
    def order(self):
        return self.raw_order.split(",")

    @property
    def length(self):
        return len(self.animation)

    @property
    def initial_pose(self):
        return Pose({name: coords.coords for name, coords in zip(self.order, self.skeleton)})
