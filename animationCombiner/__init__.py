"""Core module of the plugin"""
import bpy
from bpy.props import BoolProperty
from bpy.types import AddonPreferences

from animationCombiner import registry

bl_info = {
    "name": "Animation Combiner",
    "author": "phala",
    "description": "Blender plugin for crafting new animations from existing ones",
    "version": (0, 0, 1),
    "blender": (3, 0, 0),
    "location": "View3D -> AnimationCombiner",
    "warning": "",
    "category": "Animation",
}

PREFERENCES = bpy.context.preferences.addons[__name__].preferences


def register():
    """Register all custom classes"""
    registry.init()
    registry.register()


def unregister():
    """Unregister all custom classes"""
    registry.unregister()

