import bpy
from bpy.types import UIList, Operator, CollectionProperty, Panel, Context

from animationCombiner.utils import on_actions_update
from animationCombiner.ui.action import ActionPanel
from animationCombiner.ui.table_controls import BaseControlsMixin, BaseDeleteItem, BaseMoveItem
from animationCombiner.utils.weakget import weakget


class GroupsUIList(UIList):
    bl_idname = "AC_UL_groups"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, **kwargs):
        slot = item
        ma = slot
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            if ma:
                row = layout.row(align=True)
                row.prop(ma, "name", text="", emboss=False, icon="ERROR" if ma.errors else "NONE", expand=True)
                column = row.column(align=True)
                column.enabled = False
                column.prop(
                    ma,
                    "actions_count",
                    text="",
                    emboss=False,
                    icon_value=icon,
                    expand=False,
                )
                column = layout.column(align=True)
                column.enabled = False
                column.prop(
                    ma,
                    "length",
                    text="",
                    emboss=False,
                    icon_value=icon,
                    expand=False,
                )
            else:
                layout.label(text="", translate=False, icon_value=icon)
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text="", icon_value=icon)


class GroupsControlsMixin(BaseControlsMixin):
    """Specific Control class for ActionList"""

    @property
    def active(self):
        return bpy.context.object.data.active

    @active.setter
    def active(self, active):
        bpy.context.object.data.active = active

    def callback(self):
        on_actions_update()

    @property
    def list(self) -> CollectionProperty:
        return bpy.context.object.data.groups


class AddGroupOperator(GroupsControlsMixin, Operator):
    """Add Item Operator for Groups"""

    bl_idname = "ac.groups_add"
    bl_label = "Adds item to the list"

    def execute(self, context):
        group = self.list.add()
        group.name = f"Group {len(self.list)}"

        return {"FINISHED"}


class DeleteGroupOperator(GroupsControlsMixin, BaseDeleteItem, Operator):
    """Delete Item Operator for Groups"""

    bl_idname = "ac.groups_delete_item"

    def execute(self, context):
        index = self.active
        result = super().execute(context)
        if index != self.active:
            bpy.context.object.data.move_to_group = self.active
        return result


class MoveGroupOperator(GroupsControlsMixin, BaseMoveItem, Operator):
    """Move Item Operator for Groups"""

    bl_idname = "ac.groups_move_item"


class GroupListPanel(Panel):
    bl_label = "Group list"
    bl_idname = "AC_PT_group_list"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = ActionPanel.bl_idname
    bl_order = 5

    @classmethod
    def poll(cls, context):
        return weakget(context).object.type % "NONE" == "ARMATURE" and weakget(context).object.data % False

    def draw(self, context: Context) -> None:
        layout = self.layout
        layout.use_property_split = True
        obj = context.object.data

        row = layout.row(align=True)
        row.label(text="Final length")
        col = row.column()
        col.enabled = False
        col.prop(obj, "animation_length", slider=False, text="")

        row = layout.row(align=True)
        row.label(text="Name")
        row.label(text="Actions")
        row.label(text="Length")
        layout.template_list(GroupsUIList.bl_idname, "", obj, "groups", obj, "active", sort_lock=True)
        layout.separator()

        col = layout.column().column_flow(columns=2, align=True)
        col.operator(AddGroupOperator.bl_idname, text="Add", icon="ADD")
        col.operator(DeleteGroupOperator.bl_idname, text="Delete", icon="REMOVE")
        col.operator(MoveGroupOperator.bl_idname, text="Up", icon="TRIA_UP").direction = "UP"
        col.operator(MoveGroupOperator.bl_idname, text="Down", icon="TRIA_DOWN").direction = "DOWN"
