import typing

import bpy
from bpy.props import StringProperty
from bpy.types import Context

from animationCombiner.utils import copy, on_actions_update


class Empty(bpy.types.Operator):
    """Placeholder for some future operator."""

    bl_idname = "ac.empty"
    bl_label = "Empty Action"


class RunAnimationOperator(bpy.types.Operator):
    """Plays/Stops the animation."""

    bl_idname = "ac.run"
    bl_label = "Run Animation"

    def execute(self, context: Context) -> typing.Set[str]:
        return bpy.ops.screen.animation_play()


class BackToStartOperator(bpy.types.Operator):
    """Returns animation playback to the start."""

    bl_idname = "ac.back_to_start"
    bl_label = "Back to start"

    def execute(self, context: Context) -> typing.Set[str]:
        return bpy.ops.screen.frame_jump(end=False)


class SelectObjectOperator(bpy.types.Operator):
    bl_idname = "ac.select_name"
    bl_label = "Selects a armature by name"

    name: StringProperty(name="Armature Name")

    def execute(self, context: Context) -> typing.Set[str]:
        bpy.context.view_layer.objects.active = bpy.data.objects[self.name]
        bpy.ops.object.mode_set(mode="POSE")
        return {"FINISHED"}


class MoveActionToGroupOperator(bpy.types.Operator):
    bl_idname = "ac.move_action_group"
    bl_label = "Move action to specific group"

    def execute(self, context: Context) -> typing.Set[str]:
        obj = context.object.data
        if obj.active == obj.move_to_group:
            return {"CANCELLED"}

        group = obj.groups[obj.active]
        action = group.actions[group.active]

        new_group = obj.groups[obj.move_to_group]
        new_action = new_group.actions.add()
        copy(action, new_action)

        group.actions.remove(group.active)
        group.active = min(max(0, group.active - 1), len(group.actions) - 1)
        on_actions_update()
        return {"FINISHED"}


class SelectGroupOperator(bpy.types.Operator):
    bl_idname = "ac.select_action_group"
    bl_label = "Select group to which the action will be moved"

    name: StringProperty(name="Group Name")

    def execute(self, context: Context) -> typing.Set[str]:
        obj = context.object.data
        for index, group in enumerate(context.object.data.groups):
            if group.name == self.name:
                obj.move_to_group = index
                return {"FINISHED"}
        self.report({"ERROR"}, f"Unable to find group called {self.name}")
        return {"CANCELLED"}


class SelectAllPartsOperator(bpy.types.Operator):
    """Selects all body parts"""

    bl_idname = "ac.select_all_parts"
    bl_label = "Selects all body parts"

    def execute(self, context: Context) -> typing.Set[str]:
        group = context.object.data.groups[context.object.data.active]
        action = group.actions[group.active]
        for part in action.body_parts:
            part.checked = True
        return {"FINISHED"}


class SelectNoPartsOperator(bpy.types.Operator):
    """Selects no body parts"""

    bl_idname = "ac.select_no_parts"
    bl_label = "Selects no body parts"

    def execute(self, context: Context) -> typing.Set[str]:
        group = context.object.data.groups[context.object.data.active]
        action = group.actions[group.active]
        for part in action.body_parts:
            part.checked = False
        return {"FINISHED"}
