from typing import Set

import bpy
from bpy.props import EnumProperty
from bpy.types import Context

from animationCombiner.operators import RunAnimationOperator, BackToStartOperator, CreateExampleOperator


class MainPanel(bpy.types.Panel):
    """Parent panel for the entire plugin."""
    bl_label = "AnimationCombiner"
    bl_idname = "AC_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AnimationCombiner"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Master Panel")


class ControlPanel(bpy.types.Panel):
    """Contains playback related settings/controls."""

    bl_label = "Controls"
    bl_idname = "AC_PT_controls"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = MainPanel.bl_idname
    bl_order = 10

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        if bpy.context.screen.is_animation_playing:
            row.operator(RunAnimationOperator.bl_idname, text="Stop", icon="PAUSE")
        else:
            row.operator(RunAnimationOperator.bl_idname, text="Play", icon="PLAY")
        row.operator(BackToStartOperator.bl_idname, text="Back To Start", icon="PREV_KEYFRAME")
        row = col.row(align=True).split(factor=0.2)
        row.label(text="FPS")
        row.prop(bpy.context.scene.render, "fps", text="", slider=True)


class ArmatureSelect(bpy.types.Menu):
    bl_idname = "AC_MT_armatures_select"
    bl_label = "Select armature"

    def draw(self, context):
        objects = bpy.data.armatures

        layout = self.layout
        for armature in objects:
            text = armature.name
            layout.operator("ac.select_name", text=text).name = text


class CreateSkeletonOperator(bpy.types.Operator):
    bl_idname = "ac.create_skeleton"
    bl_label = "Creates new skeleton"

    def eval_attr(self, object, name):
        resolved = object
        for o in name.split("."):
            resolved = getattr(resolved, o)
        return resolved

    def execute(self, context: Context) -> Set[str]:
        self.eval_attr(bpy.ops, context.scene.preset)()
        return {"FINISHED"}


def create_items(presets):
    items = []
    for preset in presets:
        items.append((preset[0], preset[1], f"Creates {preset[1]} base skeleton"))
    return items


class SelectPanel(bpy.types.Panel):
    bl_label = "Armature Select"
    bl_idname = "AC_PT_armature"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = MainPanel.bl_idname
    bl_order = 5

    SKELETONS = [
        (CreateExampleOperator.bl_idname, "HBM05")
    ]

    @classmethod
    def register(cls):
        bpy.types.Scene.preset = EnumProperty(
            items=create_items(cls.SKELETONS),
            name="Presets",
            default=cls.SKELETONS[0][0]
        )

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.preset

    def draw(self, context):
        row = self.layout.row()
        row.prop(bpy.context.scene, "preset")
        row.operator(CreateSkeletonOperator.bl_idname, text="Create Armature")

        row = self.layout.row()
        row.label(text="Select: ")
        text = context.object.name if context.object.type == "ARMATURE" else "None"
        row.menu(ArmatureSelect.bl_idname, text=text)
