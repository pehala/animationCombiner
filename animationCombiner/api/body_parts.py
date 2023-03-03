from uuid import uuid4

from bpy.props import StringProperty, CollectionProperty, IntProperty
from bpy.types import PropertyGroup


class Bone(PropertyGroup):
    bone: StringProperty()


class BodyPart(PropertyGroup):
    bones: CollectionProperty(type=Bone)
    name: StringProperty()
    uuid: StringProperty()
    active: IntProperty()

    def get_uuid(self):
        if not self.uuid:
            self.uuid = str(uuid4())
        return self.uuid


class BodyPartsConfiguration(PropertyGroup):
    body_parts: CollectionProperty(type=BodyPart)
