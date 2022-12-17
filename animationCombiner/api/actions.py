import bpy

from animationCombiner.registry import AutoRegister


class Action(bpy.types.PropertyGroup, AutoRegister):
    name: bpy.props.StringProperty(name="Name", default="Unknown")
    value: bpy.props.IntProperty(name="Value", default=22)

    @classmethod
    def register(cls):
        bpy.types.Armature.actions = bpy.props.CollectionProperty(type=Action)
        bpy.types.Armature.active = bpy.props.IntProperty(name="active", default=0)
