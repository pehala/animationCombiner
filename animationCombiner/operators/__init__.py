import typing

import bpy
from bpy.props import StringProperty
from bpy.types import Context

from animationCombiner.animation import create_armature
from animationCombiner.api.actions import on_actions_update
from animationCombiner.utils import copy


class CreateArmatureOperator(bpy.types.Operator):
    """Creates HBM skeleton as a base"""

    bl_idname = "ac.create_example"
    bl_label = "Create empty armature"

    @staticmethod
    def run(self, context):
        self.layout.operator(CreateArmatureOperator.bl_idname)

    @classmethod
    def register(cls):
        bpy.types.VIEW3D_MT_add.prepend(cls.run)

    @classmethod
    def unregister(cls):
        bpy.types.VIEW3D_MT_add.remove(cls.run)

    def execute(self, context):
        create_armature(context.scene.armature_name_preset)
        return {"FINISHED"}


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
