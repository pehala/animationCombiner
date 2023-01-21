import math
import typing
from importlib import resources

import bpy
from bpy.types import Context

from animationCombiner.animation import create_armature
from animationCombiner.parsers.messif import HDM05MessifLoader


class CreateExampleOperator(bpy.types.Operator):
    """Creates HBM skeleton as a base"""
    bl_idname = "ac.create_example"
    bl_label = "Create HBM skeleton"

    @staticmethod
    def run(self, context):
        self.layout.operator(CreateExampleOperator.bl_idname)

    @classmethod
    def register(cls):
        bpy.types.VIEW3D_MT_add.prepend(cls.run)

    @classmethod
    def unregister(cls):
        bpy.types.VIEW3D_MT_add.remove(cls.run)

    def execute(self, context):
        with resources.files("animationCombiner.resources").joinpath("test.data").open("r") as file:
            loader = HDM05MessifLoader(file, "test")
        armature = create_armature(loader.load_skeletons()[0])
        armature.rotation_mode = "XYZ"
        armature.rotation_euler.rotate_axis("X", math.radians(90))

        bpy.ops.wm.context_toggle(data_path="space_data.show_region_ui")
        bpy.ops.object.mode_set(mode='POSE')
        return {"FINISHED"}


class Empty(bpy.types.Operator):
    """Placeholder for some future operator."""
    bl_idname = "ac.empty"
    bl_label = "Empty Action"


class RunAnimationOperator(bpy.types.Operator):
    """Plays/Stops the animation."""
    bl_idname = "ac.run"
    bl_label = "Run Animation"

    def execute(self, context: Context) -> typing.Set[str]:
        return bpy.ops.screen.animation_play()


class BackToStartOperator(bpy.types.Operator):
    """Returns animation playback to the start."""
    bl_idname = "ac.back_to_start"
    bl_label = "Back to start"

    def execute(self, context: Context) -> typing.Set[str]:
        return bpy.ops.screen.frame_jump(end=False)
