"""Module containing all Operators related to Importing actions"""
import os

import bpy
from bpy.props import StringProperty, CollectionProperty, BoolProperty
from bpy.types import Context
from bpy_extras.io_utils import ImportHelper

from animationCombiner.api.actions import EnabledPartsCollection
from animationCombiner.api.body_parts import BodyPartsConfiguration
from animationCombiner.utils import on_actions_update, copy
from animationCombiner.api.skeletons import HDMSkeleton
from animationCombiner.parsers import ParserError, load_animation_from_path, PARSERS
from animationCombiner.utils.coordinates import invert_yz


class ImportActionOperator(bpy.types.Operator, ImportHelper):
    """Imports new action"""

    bl_label = "Import file"
    bl_idname = "ac.file_selector"

    filename_ext = ".data"
    hide_props_region = True
    filter_glob: StringProperty(
        default="",
        options={"HIDDEN"},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )
    body_parts: CollectionProperty(type=EnabledPartsCollection)
    invert_yz: BoolProperty(
        name="Use Y for height",
        description="In Blender Z coordinate is height, set to true if the input file uses Y for height. It does not "
        "affect functionality, it just improves how it is displayed in Blender.",
    )

    def generate_parts(self, config: BodyPartsConfiguration):
        self.body_parts.clear()
        for part in config.body_parts:
            new_part = self.body_parts.add()
            new_part.name = part.name
            new_part.uuid = part.get_uuid()

    def invoke(self, context, _event):
        self.filter_glob = "*" + ";*".join(PARSERS.keys())
        self.generate_parts(bpy.context.view_layer.objects.active.data.get_body_parts())
        return super().invoke(context, _event)

    def execute(self, context):
        try:
            path = self.properties.filepath
            raw_animation = load_animation_from_path(path)
            if self.invert_yz:
                invert_yz(raw_animation)

            armature = bpy.context.view_layer.objects.active.data

            action = armature.groups[armature.active].actions.add()
            if len(armature.groups) == 1 and len(armature.groups[armature.active].actions) == 1:
                action.use_skeleton = True
            copy(self.body_parts, action.body_parts)
            action.animation.from_raw(raw_animation, HDMSkeleton())
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

    def draw(self, context: Context) -> None:
        layout = self.layout

        layout.prop(data=self, property="invert_yz")
        layout.label(text="Body Parts:")
        box = layout.box()
        columns = box.column_flow(columns=2, align=True)
        for part in self.body_parts:
            columns.prop(part, "checked", text=part.name)
