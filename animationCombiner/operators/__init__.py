import math
import typing
from importlib import resources

import bpy
from bpy.types import Context

from animationCombiner.animation import create_armature
from animationCombiner.parsers import HDM05MessifLoader
from animationCombiner.registry import AutoRegister


class CreateExampleOperator(bpy.types.Operator, AutoRegister):
    bl_idname = "ac.CreateExample"
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
            loader = HDM05MessifLoader(file)
        armature = create_armature(loader.load_skeleton())
        armature.rotation_mode = "XYZ"
        armature.rotation_euler.rotate_axis("X", math.radians(90))

        bpy.ops.wm.context_toggle(data_path="space_data.show_region_ui")
        return {"FINISHED"}


class Empty(bpy.types.Operator, AutoRegister):
    bl_idname = "wm.empty"
    bl_label = "Empty Action"


class RunAnimationOperator(bpy.types.Operator, AutoRegister):
    bl_idname = "wm.run"
    bl_label = "Run Animation"

    def execute(self, context: Context) -> typing.Set[str]:
        return bpy.ops.screen.animation_play()


class BackToStartOperator(bpy.types.Operator, AutoRegister):
    bl_idname = "wm.back_to_start"
    bl_label = "Back to start"

    def execute(self, context: Context) -> typing.Set[str]:
        return bpy.ops.screen.frame_jump(end=False)
