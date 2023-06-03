"""Module containing all Operators related to Importing actions"""
import os
from typing import Iterable

import bpy
from bpy.props import CollectionProperty, BoolProperty
from bpy.types import Context, Operator
from bpy_extras.io_utils import ImportHelper

from animationCombiner.api.actions import EnabledPartsCollection
from animationCombiner.api.body_parts import BodyPartsConfiguration
from animationCombiner.api.model import RawAnimation
from animationCombiner.utils import on_actions_update, copy
from animationCombiner.api.skeletons import HDMSkeleton
from animationCombiner.parsers.error import ParserError
from animationCombiner.utils.coordinates import invert_yz


class BaseImportOperator(Operator, ImportHelper):
    """Imports new action"""

    bl_idname = "ac.base_import_file"
    bl_label = "Import"

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
        self.generate_parts(bpy.context.view_layer.objects.active.data.get_body_parts())
        return super().invoke(context, _event)

    def execute(self, context):
        try:
            path = self.properties.filepath
            with open(path, "r") as file:
                raw_animation = self.load_animation(file)

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

    def load_animation(self, file) -> RawAnimation:
        """Loads & returns iterable of transition to achieve the animation"""
        return next(iter(self.load_animations(file)))

    def load_animations(self, file) -> Iterable[RawAnimation]:
        """Returns all animations that are present in the file"""
