"""Animation processing module"""
import bpy
import numpy as np

from .api.model import Pose, Bone, Animation


def create_bone(armature, joint: Bone):
    """Create Blender Bone"""
    bone = armature.data.edit_bones.new(joint.name)
    if joint.parent:
        bone.head = joint.parent.pos
        bone.tail = joint.pos
        joint.pos = joint.pos
        bone.parent = joint.parent.bone
    else:
        bone.head = np.array((0, 0.1, 0))
        bone.tail = joint.pos
        joint.pos = joint.pos

    joint.bone = bone


def create_armature(pose: Pose):
    """Create the entire Armature"""
    armature = bpy.data.armatures.new("Armature")
    action = armature.actions.add()
    action.name = "Step"
    action.value = 1000
    action = armature.actions.add()
    action.name = "Punch"
    action.value = 1000
    armature_object = bpy.data.objects.new("Armature", armature)
    # Link armature object to our scene
    collection = bpy.data.collections.new("My Collection")
    bpy.context.scene.collection.children.link(collection)
    layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
    bpy.context.view_layer.active_layer_collection = layer_collection

    collection.objects.link(armature_object)

    # Make a coding shortcut
    armature_data = bpy.data.objects[armature_object.name]
    bpy.context.view_layer.update()

    # Must make armature active and in edit mode to create a bone
    bpy.context.view_layer.objects.active = armature_data
    armature_data.select_set(state=True)
    bpy.ops.object.mode_set(mode="EDIT", toggle=False)

    queue = [pose.root]
    while len(queue) > 0:
        bone = queue.pop()
        create_bone(armature_data, bone)
        queue.extend(bone.children)

    # Exit Armature editing
    bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
    return armature_data


def process_animation(armature, animation: Animation, frame_delay=1, frame_start=0, reset=False, reset_duraration=10):
    """Test"""
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode="POSE")
    for name in animation.pose.bones.keys():
        bone = armature.pose.bones[name]
        bone.rotation_mode = "QUATERNION"
        bone.keyframe_insert(
            data_path="rotation_quaternion",
            frame=frame_start,
        )
    last_frame = 0
    for i, frame in enumerate(animation.transitions):
        for name, quaternion in frame.bones.items():
            bone = armature.pose.bones[name]
            bone.rotation_quaternion = quaternion
            bone.keyframe_insert(
                data_path="rotation_quaternion",
                frame=frame_start + (i * frame_delay),
            )
        last_frame = frame_start + (i * frame_delay)
    # if reset:
    #     for name, vector in animation.pose.bones.items():
    #         bone = armature.pose.bones[name]
    #         bone.rotation_quaternion = bone.tail.rotation_difference(vector)
    #         bone.keyframe_insert(
    #             data_path='rotation_quaternion',
    #             frame=last_frame + reset_duraration
    #         )
    #     last_frame = last_frame + reset_duraration
    return last_frame + 1
