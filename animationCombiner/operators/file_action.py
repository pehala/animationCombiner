import os

import bpy
from bpy.props import StringProperty, PointerProperty
from bpy_extras.io_utils import ImportHelper

from animationCombiner.api.actions import LengthGroup
from animationCombiner.parsers import find_parser_for_path, ParserError


class IdentifierFileSelector(bpy.types.Operator, ImportHelper):
    bl_label = "File Browser"
    bl_idname = "ac.file_selector"

    def execute(self, context):
        bpy.ops.ac.custom_confirm_dialog('INVOKE_DEFAULT', path=self.properties.filepath)
        # context.window_manager.invoke_props_dialog(bpy.ops.ac.custom_confirm_dialog)
        return {'FINISHED'}


class SimplePropConfirmOperator(bpy.types.Operator):
    """Really?"""
    bl_idname = "ac.custom_confirm_dialog"
    bl_label = "Pick file"
    bl_options = {'REGISTER', 'INTERNAL'}

    path: StringProperty(name="Path")
    length: PointerProperty(type=LengthGroup)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        print("self")
        armature = bpy.data.armatures[bpy.context.view_layer.objects.active.name]
        action = armature.actions.add()
        action.name = os.path.basename(self.path)
        action.path = self.path
        action.length_group.apply(self.length)
        self.report({'INFO'}, "Imported 1 action")
        return {'FINISHED'}

    def invoke(self, context, event):
        try:
            self.parser = find_parser_for_path(self.path)
            with open(self.path, "r") as file:
                self.length.original_length = self.parser(file, self.path).scrub_file()
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

