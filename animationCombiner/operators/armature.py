import bpy

from animationCombiner.utils import create_armature


class CreateArmatureOperator(bpy.types.Operator):
    """Creates HBM skeleton as a base"""

    bl_idname = "ac.create_example"
    bl_label = "Create empty armature"

    @staticmethod
    def run(self, context):
        self.layout.operator(CreateArmatureOperator.bl_idname)

    @classmethod
    def register(cls):
        bpy.types.VIEW3D_MT_add.prepend(cls.run)

    @classmethod
    def unregister(cls):
        bpy.types.VIEW3D_MT_add.remove(cls.run)

    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
        create_armature(context.scene.armature_name_preset)
        bpy.ops.ac.groups_add()
        return {"FINISHED"}
