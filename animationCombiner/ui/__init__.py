import bpy
from bpy.types import Context

from animationCombiner.operators import RunAnimationOperator, BackToStartOperator
from animationCombiner.operators.files.export import ExportSomeData
from animationCombiner.operators.files.importer import ImportActionOperator


class MainPanel(bpy.types.Panel):
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
    """Creates a Panel in the Object properties window"""

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
        row.operator(RunAnimationOperator.bl_idname, text="Play", icon="PLAY")
        row.operator(BackToStartOperator.bl_idname, text="Back To Start", icon="PREV_KEYFRAME")


class ImportPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""

    bl_label = "Import/Export"
    bl_idname = "AC_PT_import_export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = MainPanel.bl_idname

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator(ImportActionOperator.bl_idname, text="Import", icon="IMPORT")
        row.operator(ExportSomeData.bl_idname, text="Export", icon="EXPORT")
