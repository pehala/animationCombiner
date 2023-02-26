from bpy.props import StringProperty, CollectionProperty, IntProperty
from bpy.types import PropertyGroup


class Bone(PropertyGroup):
    bone: StringProperty()


class BodyPart(PropertyGroup):
    bones: CollectionProperty(type=Bone)
    name: StringProperty()
    active: IntProperty()


class BodyPartsConfiguration(PropertyGroup):
    body_parts: CollectionProperty(type=BodyPart)
