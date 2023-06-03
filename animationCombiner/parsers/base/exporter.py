from typing import Collection, Set

import bpy
from bpy.props import CollectionProperty, BoolProperty
from bpy.types import Operator, Context, Event
from bpy_extras.io_utils import ExportHelper
from mathutils import Vector

from animationCombiner.api.actions import EnabledPartsCollection
from animationCombiner.api.body_parts import BodyPartsConfiguration
from animationCombiner.api.model import RawAnimation, Pose
from animationCombiner.utils.coordinates import invert_yz


class BaseExportOperator(Operator, ExportHelper):
    """Exports the animation data. Need to be processed first"""

    bl_idname = "ac.base_export_file"
    bl_label = "Export"

    invert_yz: BoolProperty(
        name="Use Y for height",
        description="In Blender Z coordinate is height, set to true if the input file uses Y for height. It does not "
        "affect functionality, it just improves how it is displayed in Blender.",
    )
    body_parts: CollectionProperty(type=EnabledPartsCollection)

    def generate_parts(self, config: BodyPartsConfiguration):
        self.body_parts.clear()
        for part in config.body_parts:
            new_part = self.body_parts.add()
            new_part.name = part.name
            new_part.uuid = part.get_uuid()

    def invoke(self, context: Context, event: Event) -> Set[str]:
        self.generate_parts(bpy.context.view_layer.objects.active.data.body_parts)
        return super().invoke(context, event)

    def execute(self, context):
        armature = bpy.context.view_layer.objects.active

        config = armature.data.body_parts
        disabled_parts = {part.uuid for part in self.body_parts if not part.checked}

        disabled_bones = set()
        for part in config.body_parts:
            if part.uuid in disabled_parts:
                for bone in part.bones:
                    disabled_bones.add(bone.bone)

        # curves = {}
        # for fcurve in armature.animation_data.action.fcurves:
        #     name = fcurve.data_path.split('"')[1]
        #     curves.setdefault(name, []).append(fcurve)
        #
        # for bone_curves in curves.values():
        #     bone_curves.sort(key=lambda c: c.array_index)

        transitions = []
        for frame in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end):
            bpy.context.scene.frame_set(frame)
            bones = {}
            for bone in armature.pose.bones:
                bones[bone.name] = bone.tail.copy()
            for bone in disabled_bones:
                bones[bone] = Vector((0, 0, 0))
            transitions.append(Pose(bones))
        bpy.context.scene.frame_set(bpy.context.scene.frame_start)
        data = RawAnimation(transitions, None)
        if self.invert_yz:
            invert_yz(data)

        with open(self.filepath, "w") as file:
            self.export_animation(data, disabled_bones, file)
        return {"FINISHED"}

    def export_animation(self, animation: RawAnimation, disabled_bones: Collection[str], file):
        """Writes animation to a file, kwargs are for"""

    def draw(self, context: Context) -> None:
        layout = self.layout

        layout.prop(data=self, property="invert_yz")
        layout.label(text="Enabled Body Parts:")
        box = layout.box()
        columns = box.column_flow(columns=2, align=True)
        for part in self.body_parts:
            columns.prop(part, "checked", text=part.name)
