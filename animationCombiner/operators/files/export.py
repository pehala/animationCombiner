import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper
from mathutils import Quaternion, Vector

from animationCombiner.api.model import Pose, RawAnimation
from animationCombiner.parsers import find_exporter_for_path


def to_quaternion(curves, frame):
    return Quaternion(Vector(curves[i].evaluate(frame) for i in range(3)), curves[3].evaluate(frame))


class ExportSomeData(bpy.types.Operator, ExportHelper):
    """Exports the animation data. Need to be processed first"""
    bl_idname = "ac.export_file"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Animation"

    # ExportHelper mixin class uses this
    filename_ext = ".data"

    filter_glob: StringProperty(
        default="*.data",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        exporter = find_exporter_for_path(self.filepath)()

        armature = bpy.context.view_layer.objects.active
        curves = {}
        for fcurve in armature.animation_data.action.fcurves:
            name = fcurve.data_path.split('"')[1]
            curves.setdefault(name, []).append(fcurve)

        for bone_curves in curves.values():
            bone_curves.sort(key=lambda c: c.array_index)

        transitions = []
        for frame in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end):
            bpy.context.scene.frame_set(frame)
            bones = {}
            for bone in armature.pose.bones:
                bones[bone.name] = bone.tail.copy()
            transitions.append(Pose(bones))
        bpy.context.scene.frame_set(bpy.context.scene.frame_start)
        with open(self.filepath, "w") as file:
            exporter.export_animation(RawAnimation(transitions, None), file)
        return {"FINISHED"}
