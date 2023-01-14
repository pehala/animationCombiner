import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper
from mathutils import Quaternion, Vector

from animationCombiner.api.model import Transition
from animationCombiner.parsers import find_exporter_for_path


def to_quaternion(curves, frame):
    return Quaternion(Vector(curves[i].evaluate(frame) for i in range(3)), curves[3].evaluate(frame))


class ExportSomeData(bpy.types.Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "ac.export_file"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Animation"

    # ExportHelper mixin class uses this
    filename_ext = ".data"

    filter_glob: StringProperty(
        default="*.txt",
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

        # bpy.context.scene.frame_set(bpy.context.scene.frame_start)
        # transitions = []
        # for frame in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end):
        #     bones = {}
        #     for bone in armature.pose.bones:
        #         pos = bone.tail.copy()
        #         pos.rotate(to_quaternion(curves[bone.name], frame))
        #         bones[bone.name] = pos
        #     transitions.append(Transition(bones))
        transitions = []
        for frame in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end):
            bpy.context.scene.frame_set(frame)
            bones = {}
            for bone in armature.pose.bones:
                # pos = bone.tail.copy()
                # pos.rotate(to_quaternion(curves[bone.name], frame))
                bones[bone.name] = bone.tail.copy()
            transitions.append(Transition(bones))
        bpy.context.scene.frame_set(bpy.context.scene.frame_start)
        with open(self.filepath, "w") as file:
            exporter.export_animations(transitions, file)
        return {"FINISHED"}
