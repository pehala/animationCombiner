"""Core module of the plugin"""
import bpy

from animationCombiner import registry

bl_info = {
    "name": "Animation Combiner",
    "author": "phala",
    "description": "Blender plugin for crafting new animations from existing ones",
    "version": (0, 1, 0),
    "blender": (3, 0, 0),
    "location": "View3D -> AnimationCombiner",
    "warning": "",
    "doc_url": "https://github.com/pehala/animationCombiner",
    "tracker_url": "https://github.com/pehala/animationCombiner/issues",
    "category": "Animation",
}


def get_preferences():
    return bpy.context.preferences.addons[__name__].preferences


def register():
    """Register all custom classes"""
    registry.init()
    registry.register()


def unregister():
    """Unregister all custom classes"""
    registry.unregister()
