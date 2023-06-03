from typing import Collection

import numpy
import numpy as np
from bpy.props import StringProperty
from bpy.types import Operator
from mathutils import Vector

from animationCombiner.api.model import Pose, RawAnimation
from animationCombiner.api.skeletons import HDMSkeleton
from animationCombiner.parsers import importers
from animationCombiner.parsers.base.importer import BaseImportOperator
from animationCombiner.parsers.messif import NAMES


@importers.register(name="MESSIF, HDM05 (.data)")
class MessifLoader(BaseImportOperator, Operator):
    bl_idname = "ac.messif_import_file"

    # ExportHelper mixin class uses this
    filename_ext = ".data"

    filter_glob: StringProperty(
        default="*.data",
        options={"HIDDEN"},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def parse(self, file):
        animations = []
        animation = []
        i = 0

        while line := file.readline():
            i += 1
            if line.startswith("#objectKey"):
                if len(animation) > 0:
                    animations.append(animation)
                animation = []
                # ignore type line
                file.readline()
                i += 1
            else:
                animation.append(self.parse_skeleton(line, i))
        if len(animation) > 0:
            animations.append(animation)
        return animations

    def load_animations(self, file) -> Collection[RawAnimation]:
        animations = []
        for animation in self.parse(file):
            animations.append(RawAnimation(animation, HDMSkeleton()))
        return animations

    def parse_skeleton(self, line, line_number):
        bones = {}
        vectors = line.split(";")
        assert len(vectors) == len(NAMES), f"Incompatible skeleton at line {line_number}"
        for i, vector in enumerate(vectors):
            numbers = vector.split(",")
            assert len(numbers) == 3, f"Incorrect vector dimensions at line {line_number}"
            bones[NAMES[i]] = Vector(np.asarray(numbers, dtype=numpy.double))
        return Pose(bones=bones)
