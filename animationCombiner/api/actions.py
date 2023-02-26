from math import ceil

import bpy
from bpy.props import (
    IntProperty,
    FloatProperty,
    StringProperty,
    PointerProperty,
    BoolProperty,
)

from animationCombiner.api.animation import Animation


def on_actions_update(self=None, context=None):
    """Recalculates length of final animation after the actions were updated"""
    armature = bpy.context.view_layer.objects.active.data
    length = 0
    for action in armature.actions:
        length += action.length_group.length
    armature.animation_length = length
    armature.is_applied = False


class LengthGroup(bpy.types.PropertyGroup):
    def update_length(self, context):
        expected = self.length / self.original_length
        if self.speed != expected:
            self.speed = expected
            on_actions_update()

    def update_speed(self, context):
        expected = ceil(self.original_length * self.speed)
        if self.length != expected:
            self.length = expected
            on_actions_update()

    def update_start(self, context):
        if self.start > self.length:
            self.start = self.length
        if self.start > self.end:
            self.start = self.end
        on_actions_update()

    def update_end(self, context):
        if self.end > self.length:
            self.end = self.length
        if self.end < self.start:
            self.end = self.start
        on_actions_update()

    def copy_from(self, other: "LengthGroup"):
        self.original_length = other.original_length
        self.length = other.length
        self.speed = other.speed

    original_length: IntProperty(name="Original Length", description="Original Length (in frames)")
    length: IntProperty(name="Length", description="Length (in frames)", update=update_length)
    speed: FloatProperty(
        name="Speed",
        description="Speed (compared to original)",
        default=1,
        update=update_speed,
    )
    start: IntProperty(
        name="start",
        description="On which frame should the animation start, defaults to 0",
        default=0,
        min=0,
        update=update_start,
    )
    end: IntProperty(
        name="end",
        description="On which frame should the animation end, defaults to last frame",
        min=0,
        update=update_end,
    )

    def draw(self, layout):
        layout.use_property_split = True
        row = layout.row()
        row.enabled = False
        row.prop(self, "length")
        row = layout.row()
        row.prop(self, "start")
        row = layout.row()
        row.prop(self, "end")

        # Hidden as it doesnt work yet
        # row = layout.row()
        # row.prop(self, "length")
        # row = layout.row()
        # row.prop(self, "speed", slider=False)


class TransitionGroup(bpy.types.PropertyGroup):
    reset: BoolProperty(
        name="Reset",
        description="True, if the pose should reset to the beginning pose",
        update=on_actions_update,
    )
    reset_length: IntProperty(
        name="Reset Length",
        description="Reset length (in frames)",
        update=on_actions_update,
    )
    length: IntProperty(
        name="Length",
        description="Transition length (in frames)",
        default=1,
        min=1,
        update=on_actions_update,
    )

    def draw(self, layout):
        layout.use_property_split = True
        row = layout.row()
        row.prop(self, "reset")

        row = layout.row()
        row.enabled = self.reset
        row.prop(self, "reset_length")

        row = layout.row()
        row.prop(self, "length", slider=False)

    def copy_from(self, other: "TransitionGroup"):
        self.reset = other.reset
        self.length = other.length
        self.reset_length = other.reset_length


class Action(bpy.types.PropertyGroup):
    name: StringProperty(name="Name", default="Unknown")
    length_group: PointerProperty(type=LengthGroup)
    transition: PointerProperty(type=TransitionGroup)
    animation: PointerProperty(type=Animation)

    @classmethod
    def register(cls):
        bpy.types.Armature.actions = bpy.props.CollectionProperty(type=Action)
        bpy.types.Armature.active = bpy.props.IntProperty(name="active", default=0, min=0)
        bpy.types.Armature.animation_length = bpy.props.IntProperty(
            name="animationLength",
            default=0,
            min=0,
            description="Final length in frames of the animation",
        )
        bpy.types.Armature.is_applied = bpy.props.BoolProperty(
            name="Was apply used",
            default=False,
            description="True, if the armature is up-to-date with actions",
        )

    @classmethod
    def unregister(cls):
        del bpy.types.Armature.actions
        del bpy.types.Armature.active
        del bpy.types.Armature.animation_length
        del bpy.types.Armature.is_applied

    def copy_from(self, other: "Action"):
        self.name = other.name
        self.path = other.path
        self.length_group.copy_from(other.length_group)
        self.transition.copy_from(other.transition)
        self.animation.copy_from(other.animation)

    def draw(self, layout):
        row = layout.column_flow(columns=1)
        row.prop(self, "name")

        row.label(text="Animation length settings:")
        self.length_group.draw(row.box())
        row.label(text="Transition settings:")
        self.transition.draw(row.box())
