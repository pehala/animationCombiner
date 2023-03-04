from bpy.props import IntProperty, CollectionProperty, StringProperty
from bpy.types import AddonPreferences, UIList, Operator

from animationCombiner import get_preferences
from animationCombiner.api.body_parts import BodyPartsConfiguration
from animationCombiner.ui.table_controls import BaseControlsMixin, BaseDeleteItem


class BodyPartsUIList(UIList):
    bl_idname = "AC_UL_bodyParts"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, **kwargs):
        slot = item
        ma = slot
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            if ma:
                layout.enabled = True
                layout.prop(ma, "bone", text="", emboss=False)
            else:
                layout.label(text="", translate=False, icon_value=icon)
        elif self.layout_type == "GRID":
            raise ValueError("Not supported")


DEFAULT_BODY_PARTS = {
    "Left Leg": ["lhipjoint", "lfemur", "ltibia"],
    "Right Leg": ["rhipjoint", "rfemur", "rtibia"],
    "Left Foot": ["lfoot", "ltoes"],
    "Right Foot": ["rfoot", "rtoes"],
    "Body": ["lowerback", "upperback", "thorax", "lclavicle", "rclavicle"],
    "Head": ["lowerneck", "upperneck", "head"],
    "Left Arm": ["lclavicle", "lhumerus", "lradius", "lwrist"],
    "Right Arm": ["rclavicle", "rhumerus", "rradius", "rwrist"],
    "Left Hand": ["lwrist", "lhand", "lthumb", "lfingers"],
    "Right Hand": ["rwrist", "rhand", "rthumb", "rfingers"],
}


class AnimationCombinerPreferences(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    body_parts_config: CollectionProperty(type=BodyPartsConfiguration)
    bone_parts_active: IntProperty(default=0)

    def draw(self, context):
        layout = self.layout

        layout.label(text="Body parts:")
        grid = layout.grid_flow(columns=2)
        grid.operator(AddBodyPart.bl_idname, text="Add new part", icon="ADD")
        grid.operator(ResetBodyParts.bl_idname, text="Reset", icon="ERROR")
        grid = layout.grid_flow(columns=5, even_columns=True)
        for body_part in self.body_parts:
            boxed = grid.box()
            row = boxed.row()
            row.prop(body_part, "name", text="")
            row.operator(DeleteBodyPart.bl_idname, text="", icon="REMOVE").body_part = body_part.name
            boxed.template_list(BodyPartsUIList.bl_idname, body_part.name, body_part, "bones", body_part, "active")
            col = boxed.column_flow(columns=2, align=True)
            col.operator(AddBone.bl_idname, text="", icon="ADD").body_part = body_part.name
            col.operator(DeleteBone.bl_idname, text="", icon="REMOVE").body_part = body_part.name

        # layout.prop(self, "toggle_side_menu")

    @property
    def active_config(self):
        # self.body_parts_config.clear()
        if len(self.body_parts_config) == 0:
            config = self.body_parts_config.add()
            for name, bones in DEFAULT_BODY_PARTS.items():
                body_part = config.body_parts.add()
                body_part.name = name
                for bone_name in bones:
                    bone = body_part.bones.add()
                    bone.bone = bone_name
        return self.body_parts_config[self.bone_parts_active]

    @property
    def body_parts(self):
        return self.active_config.body_parts


# Body Part controls
class ResetBodyParts(Operator):
    """Resets all bone parts to the default configuration"""

    bl_idname = "ac.body_parts_reset"
    bl_label = "Reset all body parts to a default setting"

    def execute(self, context):
        get_preferences().body_parts_config.clear()
        return {"FINISHED"}


class AddBodyPart(Operator):
    """Adds new body part"""

    bl_idname = "ac.body_parts_add"
    bl_label = "Adds body part to the list"

    def execute(self, context):
        bone = get_preferences().body_parts.add()
        bone.name = "Body Part"

        return {"FINISHED"}


class DeleteBodyPart(Operator):
    """Delete Item Operator for ActionList"""

    bl_idname = "ac.body_parts_delete"
    bl_label = "Deletes body part"

    body_part: StringProperty()

    def execute(self, context):
        if len(get_preferences().body_parts) == 1:
            self.report({"ERROR"}, "You cannot delete last body part")
            return {"CANCELLED"}
        for index, body_part in enumerate(get_preferences().body_parts):
            if body_part.name == self.body_part:
                get_preferences().body_parts.remove(index)
        return {"FINISHED"}


# Bones controls
class BoneControlsMixin(BaseControlsMixin):
    """Specific Control class for adding bones"""

    body_part: StringProperty()

    @property
    def active(self):
        for body_part in get_preferences().body_parts:
            if body_part.name == self.body_part:
                return body_part.active

    @active.setter
    def active(self, active):
        for body_part in get_preferences().body_parts:
            if body_part.name == self.body_part:
                body_part.active = active

    @property
    def list(self) -> CollectionProperty:
        for body_part in get_preferences().body_parts:
            if body_part.name == self.body_part:
                return body_part.bones


class AddBone(BoneControlsMixin, Operator):
    """Add Item Operator for bones"""

    bl_idname = "ac.body_parts_add_bone"
    bl_label = "Adds item to the list"

    def execute(self, context):
        bone = self.list.add()
        bone.bone = "New Bone"

        return {"FINISHED"}


class DeleteBone(BoneControlsMixin, BaseDeleteItem, Operator):
    """Delete Item Operator for bones"""

    bl_idname = "ac.body_parts_delete_bone"
