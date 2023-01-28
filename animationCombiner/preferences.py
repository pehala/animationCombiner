from bpy.props import BoolProperty
from bpy.types import AddonPreferences


class AnimationCombinerPreferences(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        layout.label(text="TBD")
        # layout.prop(self, "toggle_side_menu")
