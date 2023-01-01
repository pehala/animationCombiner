import bpy

from animationCombiner.animation import process_animation


class ProcessOperator(bpy.types.Operator):
    bl_idname = "ac.process"
    bl_label = "Applies all actions to the armature"

    # @staticmethod
    # def run(self, context):
    #     self.layout.operator(CreateExampleOperator.bl_idname)

    def execute(self, context):
        bpy.ops.anim.keyframe_clear_v3d()
        armature = bpy.data.armatures[bpy.context.view_layer.objects.active.name]
        ending = 0
        for action in armature.actions:
            ending = process_animation(bpy.context.view_layer.objects.active, action.animation, reset=True, frame_start=ending)
        bpy.context.scene.frame_end = ending
        return {"FINISHED"}
