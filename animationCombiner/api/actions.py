from math import ceil

import bpy
from bpy.app.handlers import persistent
from bpy.props import IntProperty, FloatProperty, StringProperty, PointerProperty

from animationCombiner.parsers import load_animation_from_path


class LengthGroup(bpy.types.PropertyGroup):
    def update_length(self, context):
        expected = self.length / self.original_length
        if self.speed != expected:
            self.speed = expected

    def update_speed(self, context):
        expected = ceil(self.original_length * self.speed)
        if self.length != expected:
            self.length = expected

    def apply(self, other: "LengthGroup"):
        self.length = other.length
        self.speed = other.speed
        self.original_length = other.original_length

    original_length: IntProperty(name="Original Length (in frames)")
    length: IntProperty(name="Length (in frames)", update=update_length)
    speed: FloatProperty(name="Speed (compared to original)", default=1, update=update_speed)

    def draw(self, layout):
        row = layout.row()
        row.enabled = False
        row.prop(self, "original_length")
        row = layout.row()
        row.prop(self, "length")
        row = layout.row()
        row.prop(self, "speed")




@persistent
def load_animations(dummy):
    for armature in bpy.data.armatures:
        for action in armature.actions:
            try:
                action._load_animation()
            except Exception as e:
                # TODO: proper error handling
                print(e)


class Action(bpy.types.PropertyGroup):

    name: StringProperty(name="Name", default="Unknown")
    path: StringProperty(name="Path to file")
    length_group: PointerProperty(type=LengthGroup)

    @classmethod
    def register(cls):
        bpy.types.Armature.actions = bpy.props.CollectionProperty(type=Action)
        bpy.types.Armature.active = bpy.props.IntProperty(name="active", default=0)
        bpy.app.handlers.load_post.append(load_animations)

    def _load_animation(self):
        self._animation = load_animation_from_path(self.path)
        self.length_group.original_length = self._animation.length
        self.length_group.length = self.length_group.original_length

    @property
    def animation(self):
        if not hasattr(self, "_animation") or self._animation is None:
            self._load_animation()
        return self._animation
