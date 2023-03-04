from enum import Enum

import bpy
from bpy.props import (
    IntProperty,
    StringProperty,
    PointerProperty,
    BoolProperty,
    CollectionProperty,
    EnumProperty,
)
from bpy.types import PropertyGroup

from animationCombiner import get_preferences
from animationCombiner.api.animation import Animation
from animationCombiner.api.body_parts import BodyPartsConfiguration
from animationCombiner.operators import SelectAllPartsOperator, SelectNoPartsOperator
from animationCombiner.utils import copy, on_actions_update


class LengthGroup(bpy.types.PropertyGroup):
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

    original_length: IntProperty(name="Original Length", description="Original Length (in frames)")
    length: IntProperty(name="Length", description="Length (in frames)")
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


def get_body_parts(self):
    if len(self.body_parts.body_parts) == 0:
        copy(get_preferences().active_config, self.body_parts)
        for group in self.groups:
            for action in group.actions:
                action.regenerate_parts(self.body_parts)
    return self.body_parts


class EnabledPartsCollection(bpy.types.PropertyGroup):
    checked: BoolProperty(name="", default=True, update=on_actions_update)
    name: StringProperty()
    uuid: StringProperty()


class Action(PropertyGroup):
    """Single action that will be applied"""

    name: StringProperty(name="Name", default="Unknown")
    length_group: PointerProperty(type=LengthGroup)
    transition: PointerProperty(type=TransitionGroup)
    animation: PointerProperty(type=Animation)
    body_parts: CollectionProperty(type=EnabledPartsCollection)

    def regenerate_parts(self, config: BodyPartsConfiguration):
        # TODO reuse existing config
        self.body_parts.clear()
        for part in config.body_parts:
            new_part = self.body_parts.add()
            new_part.name = part.name
            new_part.uuid = part.get_uuid()

    def draw(self, layout):
        row = layout.column_flow(columns=1)
        row.prop(self, "name")

        row.label(text="Animation length settings:")
        self.length_group.draw(row.box())
        row.label(text="Transition settings:")
        self.transition.draw(row.box())
        row.label(text="Body Parts settings:")
        box = row.box()
        columns = box.column_flow(columns=2, align=True)
        one_checked = False
        for part in self.body_parts:
            columns.prop(part, "checked", text=part.name)
            one_checked = one_checked or part.checked
        row = box.row(align=True)
        row.operator(SelectNoPartsOperator.bl_idname, text="Deselect All")
        row.operator(SelectAllPartsOperator.bl_idname, text="Select All")
        if not one_checked:
            box.label(text="No body parts are checked! This actions won't be applied!", icon="ERROR")


class GroupErrors(PropertyGroup):
    class Errors(Enum):
        COLLIDING_PARTS = ("Body parts are not unique", "Multiple actions apply to the same body parts")

        @classmethod
        def convert(cls):
            return [(e.name, *e.value, i) for i, e in enumerate(cls)]

    # ITEMS = [
    #     ("COLLIDING_PARTS", "Body parts are not unique", "Multiple actions apply to the same body parts", "", 1),
    #     # ("COLLIDING_PARTS", "Body parts are not unique", "Multiple actions apply to the same body parts", "", 1),
    # ]
    error: EnumProperty(items=Errors.convert())


class ActionGroup(PropertyGroup):
    """Collection of actions that will be executed at the same time"""

    actions: CollectionProperty(type=Action)
    active: IntProperty(default=0, min=0)
    length: IntProperty(default=0, min=0)
    actions_count: IntProperty(default=0, min=0)
    errors: CollectionProperty(type=GroupErrors)

    @classmethod
    def register(cls):
        bpy.types.Armature.groups = CollectionProperty(type=ActionGroup)
        bpy.types.Armature.active = IntProperty(default=0, min=0)
        bpy.types.Armature.body_parts = PointerProperty(type=BodyPartsConfiguration)
        bpy.types.Armature.get_body_parts = get_body_parts
        bpy.types.Armature.animation_length = IntProperty(
            name="animationLength",
            default=0,
            min=0,
            description="Final length in frames of the animation",
        )
        bpy.types.Armature.is_applied = BoolProperty(
            name="Was apply used",
            default=False,
            description="True, if the armature is up-to-date with actions",
        )

    @classmethod
    def unregister(cls):
        del bpy.types.Armature.groups
        del bpy.types.Armature.active
        del bpy.types.Armature.body_parts
        del bpy.types.Armature.animation_length
        del bpy.types.Armature.is_applied

    def add_error(self, error_type):
        error = self.errors.add()
        error.error = error_type
