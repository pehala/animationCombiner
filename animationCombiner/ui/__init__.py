import bpy
from bpy.props import StringProperty
from bpy.types import Context, Panel, Menu

from animationCombiner.api.actions import GroupErrors
from animationCombiner.operators import (
    RunAnimationOperator,
    BackToStartOperator,
    SelectObjectOperator,
)
from animationCombiner.operators.armature import CreateArmatureOperator
from animationCombiner.operators.files.exporter import ExportSomeData
from animationCombiner.operators.apply import ApplyOperator
from animationCombiner.utils.weakget import weakget


class MainPanel(Panel):
    """Parent panel for the entire plugin."""

    bl_label = "AnimationCombiner"
    bl_idname = "AC_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AnimationCombiner"

    def draw(self, context):
        pass
        # layout = self.layout
        # layout.label(text="Master Panel")


class ControlPanel(Panel):
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


class ArmatureSelect(Menu):
    bl_idname = "AC_MT_armatures_select"
    bl_label = "Select armature"

    def draw(self, context):
        objects = bpy.data.objects

        layout = self.layout
        for armature in objects:
            if armature.type == "ARMATURE":
                text = armature.name
                layout.operator(SelectObjectOperator.bl_idname, text=text).name = text


class SelectPanel(Panel):
    bl_label = "Armature Select"
    bl_idname = "AC_PT_armature"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = MainPanel.bl_idname
    bl_order = 5

    @classmethod
    def register(cls):
        bpy.types.Scene.armature_name_preset = StringProperty(
            name="Name", description="Name of the new armature", default="Armature"
        )

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.armature_name_preset

    def draw(self, context):
        row = self.layout.row()
        row.prop(bpy.context.scene, "armature_name_preset")
        row.operator(CreateArmatureOperator.bl_idname, text="Create Armature")

        row = self.layout.row()
        row.label(text="Select: ")
        ctx = weakget(context)
        text = context.object.name if ctx.object.type % "NONE" == "ARMATURE" else "None"
        row.menu(ArmatureSelect.bl_idname, text=text)


class ApplyPanel(Panel):
    bl_label = "Apply & Export"
    bl_idname = "AC_PT_apply_export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = MainPanel.bl_idname
    bl_context = ".posemode"
    bl_order = 30

    @classmethod
    def poll(cls, context):
        return weakget(context).object.type % "NONE" == "ARMATURE" and weakget(context).object.data % False

    def draw(self, context: Context) -> None:
        obj = context.object.data
        col = self.layout.column()
        errors = set()
        for group in obj.groups:
            for error in group.errors:
                if error.error not in errors:
                    errors.add(error.error)
                    col.label(text=GroupErrors.Errors[error.error].value[1], icon="ERROR")

        if not obj.is_applied and len(errors) == 0:
            col.label(text="Current actions were not applied yet!", icon="QUESTION")
        row = col.row()
        col = row.column()
        col.enabled = len(errors) == 0
        col.operator(ApplyOperator.bl_idname, text="Apply", icon="WORKSPACE")
        row.column().operator(ExportSomeData.bl_idname, text="Export", icon="EXPORT")
