"""Module containing all Operators related to Importing actions"""
import os

import bpy
from bpy.props import StringProperty, PointerProperty
from bpy_extras.io_utils import ImportHelper

from animationCombiner.api.actions import LengthGroup
from animationCombiner.parsers import ParserError, load_animation_from_path, PARSERS


class ImportActionOperator(bpy.types.Operator, ImportHelper):
    """Operator responsible for importing new actions"""
    bl_label = "Import file"
    bl_idname = "ac.file_selector"

    filename_ext = ".data"
    hide_props_region = True
    filter_glob: StringProperty(
        default="",
        options={"HIDDEN"},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def invoke(self, context, _event):
        self.filter_glob = "*" + ";*".join(PARSERS.keys())
        return super().invoke(context, _event)

    def execute(self, context):
        bpy.ops.ac.custom_confirm_dialog("INVOKE_DEFAULT", path=self.properties.filepath)
        return {"FINISHED"}


class ImportActionSettingsOperator(bpy.types.Operator):
    """Operator that sets properties of new actions"""

    bl_idname = "ac.custom_confirm_dialog"
    bl_label = "Pick file"
    bl_options = {"REGISTER", "INTERNAL"}

    path: StringProperty(name="Path")
    length: PointerProperty(type=LengthGroup)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        armature = bpy.data.armatures[bpy.context.view_layer.objects.active.name]
        action = armature.actions.add()
        action.name = os.path.basename(self.path)
        action.path = self.path
        action.length_group.apply(self.length)
        action._animation = self.animation
        self.report({"INFO"}, "Imported 1 action")
        return {"FINISHED"}

    def invoke(self, context, event):
        try:
            self.animation = load_animation_from_path(self.path)
            self.length.original_length = self.animation.length
            self.length.length = self.length.original_length
        except ParserError as err:
            self.report({"WARNING"}, str(err.message))
            return {"CANCELLED"}

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout.row()
        row.enabled = False
        row.prop(self, "path")
        self.length.draw(self.layout)