import bpy

from animationCombiner.animation import process_animation


class ApplyOperator(bpy.types.Operator):
    """Applies the actions to the Armature."""
    bl_idname = "ac.process"
    bl_label = "Applies all actions to the armature"

    def execute(self, context):
        bpy.ops.anim.keyframe_clear_v3d()
        armature = bpy.data.armatures[bpy.context.view_layer.objects.active.name]
        ending = 0
        for action in armature.actions:
            ending = process_animation(bpy.context.view_layer.objects.active, action.animation, reset=True, frame_start=ending)
        bpy.context.scene.frame_end = ending
        return {"FINISHED"}
