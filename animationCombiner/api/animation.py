from functools import cached_property

from bpy.props import FloatVectorProperty, CollectionProperty, StringProperty
from bpy.types import PropertyGroup
from mathutils import Vector

from animationCombiner.api.model import RawAnimation, Pose
from animationCombiner.api.skeletons import Skeleton
from animationCombiner.utils.poses import normalize_poses
from animationCombiner.utils.rotation import calculate_frames

EMPTY_VECTOR = Vector((0, 0, 0))


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

        normalized, translations = normalize_poses(raw_animation.poses)

        first_pose = normalized[0]
        for bone in skeleton.order():
            pos = self.skeleton.add()
            pos.coords = first_pose.bones[bone]

        has_translations = any(vec != EMPTY_VECTOR for vec in translations)
        if has_translations:
            for translation in translations:
                move = self.movement.add()
                move.translation = translation

        # Should fix rotation errors
        frames = calculate_frames(normalized)
        for frame in frames:
            anim = self.animation.add()
            for bone in skeleton.order():
                rotation = anim.rotations.add()
                rotation.rotation = frame[bone]

    @cached_property
    def order(self):
        return self.raw_order.split(",")

    @property
    def has_movement(self):
        return len(self.movement) > 0

    @property
    def length(self):
        return len(self.animation)

    def initial_pose(self):
        return Pose({name: coords.coords for name, coords in zip(self.order, self.skeleton)})
