import bpy
from bpy.props import CollectionProperty
from bpy.types import Operator, Panel

from animationCombiner.api.actions import on_actions_update
from animationCombiner.operators.files.export import ExportSomeData
from animationCombiner.operators.files.importer import ImportActionOperator
from animationCombiner.operators.process import ApplyOperator
from animationCombiner.ui import MainPanel
from animationCombiner.ui.table_controls import BaseControlsMixin, BaseDeleteItem, BaseMoveItem


class ActionsUIList(bpy.types.UIList):
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
                column = sub.column()
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


class ActionPanel(Panel):
    """Panel containing list of actions."""

    bl_label = "Actions"
    bl_idname = "AC_PT_actions"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = MainPanel.bl_idname
    bl_context = ".posemode"
    bl_order = 20

    @classmethod
    def poll(cls, context):
        return context.object.type == "ARMATURE"

    def draw(self, context):
        obj = context.object.data
        layout = self.layout
        layout.use_property_split = True
        layout.label(text="Actions that will be processed")
        layout.separator()
        row = layout.row().split(factor=0.4, align=True)
        row.label(text="Name")
        row.label(text="Length")
        layout.template_list(ActionsUIList.bl_idname, "", obj, "actions", obj, "active", sort_lock=True)
        layout.separator()

        col = layout.column()
        row = col.row(align=True)
        row.enabled = False
        row.label(text="Final length")
        row.prop(obj, "animation_length", slider=False, text="")

        col = layout.column_flow(columns=2, align=True)
        col.operator(ImportActionOperator.bl_idname, text="Import", icon="IMPORT")
        col.operator(ActionDeleteItem.bl_idname, text="Delete", icon="REMOVE")
        col.operator(ActionMoveItem.bl_idname, text="Up", icon="TRIA_UP").direction = "UP"
        col.operator(ActionMoveItem.bl_idname, text="Down", icon="TRIA_DOWN").direction = "DOWN"

        sublayout = layout.box()
        if obj.active >= 0 and obj.actions:
            item = obj.actions[obj.active]
            col = sublayout.column(align=True)
            col.row().label(text="Current item:")
            item.draw(col)

        layout.separator()
        col = layout.column()
        if not obj.is_applied:
            col.label(text="Current actions were not applied yet!", icon="ERROR")
        row = col.row()
        row.operator(ApplyOperator.bl_idname, text="Apply", icon="WORKSPACE")
        row.operator(ExportSomeData.bl_idname, text="Export", icon="EXPORT")


class ActionControlsMixin(BaseControlsMixin):
    """Specific Control class for ActionList"""

    @property
    def active(self):
        return bpy.context.object.data.active

    @active.setter
    def active(self, active):
        bpy.context.object.data.active = active

    @property
    def callback(self):
        return on_actions_update

    @property
    def list(self) -> CollectionProperty:
        return bpy.context.object.data.actions


class ActionDeleteItem(ActionControlsMixin, BaseDeleteItem, Operator):
    """Delete Item Operator for ActionList"""

    bl_idname = "ac.actions_delete_item"


class ActionMoveItem(ActionControlsMixin, BaseMoveItem, Operator):
    """Move Item Operator for ActionList"""

    bl_idname = "ac.actions_move_item"
