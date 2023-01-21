import bpy
from bpy.types import Context

from animationCombiner.operators import RunAnimationOperator, BackToStartOperator


class MainPanel(bpy.types.Panel):
    """Parent panel for the entire plugin."""
    bl_label = "AnimationCombiner"
    bl_idname = "AC_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Animation"
    bl_context = ".posemode"

    @classmethod
    def poll(cls, context):
        return context.object.name == "Armature"

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

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        col.prop(bpy.context.scene.render, "fps", text="FPS", slider=True)
        if bpy.context.screen.is_animation_playing:
            row.operator(RunAnimationOperator.bl_idname, text="Stop", icon="PAUSE")
        else:
            row.operator(RunAnimationOperator.bl_idname, text="Play", icon="PLAY")
        row.operator(BackToStartOperator.bl_idname, text="Back To Start", icon="PREV_KEYFRAME")
