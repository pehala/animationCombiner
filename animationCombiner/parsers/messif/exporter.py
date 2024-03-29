from random import randint
from typing import Collection, Set

from bpy.props import StringProperty, BoolProperty
from bpy.types import Context, Operator, Event

from animationCombiner.api.model import RawAnimation
from animationCombiner.parsers import exporters
from animationCombiner.parsers.base.exporter import BaseExportOperator
from animationCombiner.parsers.messif import NAMES


@exporters.register(name="MESSIF, HDM05 (.data)")
class MessifExporter(BaseExportOperator, Operator):
    bl_idname = "ac.messif_export_file"

    # ExportHelper mixin class uses this
    filename_ext = ".data"

    filter_glob: StringProperty(
        default="*.data",
        options={"HIDDEN"},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    key_id: StringProperty(
        name="Key ID", description="AbstractObjectKey ID for AbstractObjectKey. If left empty, it will be autogenerated"
    )
    attach_binary_string: BoolProperty(
        name="Attach enabled bones string",
        description="True, if the string of disabled bones should be added to the MESSIF file. This is a non-standard "
        "information, that should not break file compatiblity and will only show as a longer object id",
    )

    def invoke(self, context: Context, event: Event) -> Set[str]:
        return super().invoke(context, event)

    def draw(self, context: Context) -> None:
        super().draw(context)
        self.layout.prop(data=self, property="key_id")
        self.layout.prop(data=self, property="attach_binary_string")

    def export_animation(self, animation: RawAnimation, disabled_bones: Collection[str], file):
        binary_string = ""
        if self.attach_binary_string:
            binary_string = "".join("0" if name in disabled_bones else "1" for name in NAMES)

        key = self.key_id
        if not key:
            key = f"{randint(1000, 9999)}_{randint(10, 99)}_{randint(100, 999)}_{randint(100, 999)}"
        file.write(f"#objectKey messif.objects.keys.AbstractObjectKey {key};{binary_string}\n")
        file.write(f"{len(animation.poses)};mcdr.objects.ObjectMocapPose\n")
        for pose in animation.poses:
            data = []
            for name in NAMES:
                data.append(pose.bones[name])
            file.write("; ".join(f"{vec[0]}, {vec[1]}, {vec[2]}" for vec in data) + "\n")
