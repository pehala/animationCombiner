"""Module containing all Operators related to Importing actions"""
import os

import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper

from animationCombiner.utils import on_actions_update
from animationCombiner.api.skeletons import HBMSkeleton
from animationCombiner.parsers import ParserError, load_animation_from_path, PARSERS


class ImportActionOperator(bpy.types.Operator, ImportHelper):
    """Imports new action."""

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
        try:
            path = self.properties.filepath
            raw_animation = load_animation_from_path(path)
            armature = bpy.context.view_layer.objects.active.data
            action = armature.groups[armature.active].actions.add()
            action.regenerate_parts(armature.get_body_parts())
            action.animation.from_raw(raw_animation, HBMSkeleton())
            action.length_group.original_length = raw_animation.length
            action.length_group.length = raw_animation.length
            action.length_group.end = raw_animation.length
            action.name = os.path.basename(path)
            on_actions_update()
            self.report({"INFO"}, "Imported 1 action")
        except ParserError as err:
            self.report({"WARNING"}, str(err.message))
            return {"CANCELLED"}
        return {"FINISHED"}
