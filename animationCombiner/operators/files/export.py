import typing

import bpy
from bpy.props import StringProperty, CollectionProperty
from bpy.types import Context, Operator, Event
from bpy_extras.io_utils import ExportHelper
from mathutils import Quaternion, Vector

from animationCombiner.api.actions import EnabledPartsCollection
from animationCombiner.api.body_parts import BodyPartsConfiguration
from animationCombiner.api.model import Pose, RawAnimation
from animationCombiner.parsers import find_exporter_for_path


def to_quaternion(curves, frame):
    return Quaternion(Vector(curves[i].evaluate(frame) for i in range(3)), curves[3].evaluate(frame))


class ExportSomeData(Operator, ExportHelper):
    """Exports the animation data. Need to be processed first"""

    bl_idname = "ac.export_file"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Animation"

    # ExportHelper mixin class uses this
    filename_ext = ".data"

    filter_glob: StringProperty(
        default="*.data",
        options={"HIDDEN"},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    body_parts: CollectionProperty(type=EnabledPartsCollection)

    def generate_parts(self, config: BodyPartsConfiguration):
        self.body_parts.clear()
        for part in config.body_parts:
            new_part = self.body_parts.add()
            new_part.name = part.name
            new_part.uuid = part.get_uuid()

    def invoke(self, context: Context, event: Event) -> typing.Set[str]:
        self.generate_parts(bpy.context.view_layer.objects.active.data.body_parts)
        return super().invoke(context, event)

    def execute(self, context):
        exporter = find_exporter_for_path(self.filepath)()
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
        with open(self.filepath, "w") as file:
            exporter.export_animation(RawAnimation(transitions, None), disabled_bones, file)
        return {"FINISHED"}

    def draw(self, context: Context) -> None:
        layout = self.layout

        layout.label(text="Enabled Body Parts:")
        box = layout.box()
        columns = box.column_flow(columns=2, align=True)
        for part in self.body_parts:
            columns.prop(part, "checked", text=part.name)
