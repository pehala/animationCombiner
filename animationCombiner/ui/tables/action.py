import bpy
from bpy.props import CollectionProperty, IntProperty
from bpy.types import Operator, UIList, Panel, Context, Menu

from animationCombiner.ui.menus import ImporterMenu
from animationCombiner.utils import on_actions_update
from animationCombiner.operators import SelectGroupOperator, MoveActionToGroupOperator
from animationCombiner.ui.action import ActionPanel
from animationCombiner.ui.table_controls import BaseControlsMixin, BaseDeleteItem


class ActionsUIList(UIList):
    bl_idname = "AC_UL_actions"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, **kwargs):
        ob = data
        slot = item
        ma = slot
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            # You should always start your row layout by a label (icon + text), or a non-embossed text field,
            # this will also make the row easily selectable in the list! The later also enables ctrl-click rename.
            # We use icon_value of label, as our given icon is an integer value, not an enum ID.
            # Note "data" names should never be translated!
            if ma:
                sub = layout.split(factor=0.4, align=True)
                sub.prop(ma, "name", text="", emboss=False, icon_value=icon)
                column = sub.column(align=True)
                column.enabled = False
                column.prop(
                    ma.length_group,
                    "length",
                    text="",
                    emboss=False,
                    icon_value=icon,
                    expand=True,
                )
            else:
                layout.label(text="", translate=False, icon_value=icon)
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text="", icon_value=icon)


class ActionControlsMixin(BaseControlsMixin):
    """Specific Control class for ActionList"""

    @property
    def active(self):
        obj = bpy.context.object.data
        group = obj.groups[obj.active]
        return group.active

    @active.setter
    def active(self, active):
        obj = bpy.context.object.data
        obj.groups[obj.active].active = active

    def callback(self):
        on_actions_update()

    @property
    def list(self) -> CollectionProperty:
        obj = bpy.context.object.data
        group = obj.groups[obj.active]
        return group.actions


class DeleteActionOperator(ActionControlsMixin, BaseDeleteItem, Operator):
    """Delete Item Operator for ActionList"""

    bl_idname = "ac.actions_delete_item"


class GroupSelect(Menu):
    bl_idname = "AC_MT_group_select"
    bl_label = "Select group"

    def draw(self, context):
        objects = context.object.data.groups

        layout = self.layout
        for group in objects:
            text = group.name
            layout.operator(SelectGroupOperator.bl_idname, text=text).name = text


class ActionListPanel(Panel):
    bl_label = "Action list"
    bl_idname = "AC_PT_action_list"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = ActionPanel.bl_idname
    bl_order = 15

    @classmethod
    def register(cls):
        bpy.types.Armature.move_to_group = IntProperty(
            name="Group index", description="Index of the group to which the action should be moved", default=0
        )

    @classmethod
    def unregister(cls):
        del bpy.types.Armature.move_to_group

    def draw(self, context: Context) -> None:
        obj = context.object.data

        if not obj.groups:
            return

        group = obj.groups[obj.active]

        layout = self.layout
        layout.use_property_split = True
        row = layout.row().split(factor=0.4, align=True)
        row.label(text="Name")
        row.label(text="Length")
        layout.template_list(ActionsUIList.bl_idname, "", group, "actions", group, "active", sort_lock=True)
        layout.separator()

        row = layout.row(align=True)
        row.menu(ImporterMenu.bl_idname, text="Import", icon="IMPORT")
        row.operator(DeleteActionOperator.bl_idname, text="Delete", icon="REMOVE")

        row = layout.row(align=True)
        potential_group = obj.groups[obj.move_to_group]
        row.menu(GroupSelect.bl_idname, text=potential_group.name)
        row.operator(MoveActionToGroupOperator.bl_idname, text="Move to Group")
