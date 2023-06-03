"""Collection of all utility functions/classes that didnt fit anywhere else"""
import bpy
import typing
from bpy.types import PropertyGroup, Property, bpy_prop_collection, EditBone, Armature
from mathutils import Vector

if typing.TYPE_CHECKING:
    from animationCombiner.api.model import Pose


class Singleton(type):
    """Metaclass for Singleton markings. https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python"""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def copy(from_prop: Property, to_prop: Property, depth=0) -> None:
    if type(from_prop) != type(to_prop):
        return

    if isinstance(from_prop, PropertyGroup):
        for propname in from_prop.__annotations__.keys():
            from_subprop = getattr(from_prop, propname)
            if isinstance(from_subprop, PropertyGroup) or isinstance(from_subprop, bpy_prop_collection):
                copy(from_subprop, getattr(to_prop, propname), depth + 1)
            else:
                try:
                    setattr(to_prop, propname, from_subprop)
                # if propname == "name" and depth == 0:
                #     to_prop.name += "_copy"
                except (AttributeError, TypeError):
                    pass

    elif isinstance(from_prop, bpy_prop_collection):
        to_prop.clear()
        for from_subprop in from_prop.values():
            copy(from_subprop, to_prop.add(), depth + 1)


def on_actions_update(self=None, context=None):
    """Recalculates length of final animation after the actions were updated"""
    armature = bpy.context.view_layer.objects.active.data
    length = 0
    for group in armature.groups:
        group_length = 0
        for action in group.actions:
            if not action.enabled:
                continue
            group_length = max(action.length_group.length, group_length)
            action.length_group.length = action.length_group.real_length + action.transition.real_length
            action.length_group.update_end()
            action.length_group.update_start()
        group.length = group_length
        group.actions_count = len(group.actions)
        length += group_length
    armature.animation_length = length
    armature.is_applied = False


def complete_update(self=None, context=None):
    on_actions_update(self, context)
    update_errors(self, context)


def update_errors(self=None, context=None):
    armature = bpy.context.view_layer.objects.active.data
    use_skeleton = False
    for group in armature.groups:
        group.errors.clear()
        parts = set()
        has_movement = False
        for action in group.actions:
            if not action.enabled:
                continue
            if action.use_skeleton:
                if use_skeleton:
                    group.add_error("MULTIPLE_SKELETONS")
                use_skeleton = True
            if action.use_movement:
                if has_movement:
                    group.add_error("MULTIPLE_MOVEMENTS")
                has_movement = True
            for part in action.body_parts:
                if part.checked:
                    if part.uuid in parts:
                        group.add_error("COLLIDING_PARTS")
                        break
                    parts.add(part.uuid)
    if not use_skeleton and len(armature.groups) > 0:
        armature.groups[0].add_error("NO_SKELETONS")
    armature.is_applied = False


def create_armature(name: str = "Armature", exit_mode="POSE"):
    """Create the entire Armature"""
    bpy.ops.object.armature_add(enter_editmode=True)
    armature = bpy.context.view_layer.objects.active

    armature.name = name
    armature.data.name = name

    armature.data.edit_bones.remove(armature.data.edit_bones.get("Bone"))

    bpy.ops.object.mode_set(mode=exit_mode, toggle=False)
    return armature


def create_bone(armature, name, parent: EditBone, pose: "Pose", skeleton):
    bone = armature.edit_bones.new(name)
    bone.head = parent.tail
    bone.tail = pose.bones[name]
    bone.parent = parent

    for child in skeleton.relations.get(name, []):
        create_bone(armature, child, bone, pose, skeleton)


def create_bones(armature: Armature, skeleton, pose: "Pose", root: EditBone = None):
    if not root:
        root = armature.edit_bones.new("root")
        root.head = pose.bones["root"] + Vector((0, 0.1, 0))
        root.tail = pose.bones["root"]

    for child in skeleton.relations["root"]:
        create_bone(armature, child, root, pose, skeleton)
