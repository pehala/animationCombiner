import bpy
from bpy.types import Operator, Panel

from animationCombiner.api.actions import on_actions_update
from animationCombiner.operators.files.export import ExportSomeData
from animationCombiner.operators.files.importer import ImportActionOperator
from animationCombiner.operators.process import ApplyOperator
from animationCombiner.ui import MainPanel


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
                sub.prop(ma.length_group, "length", text="", emboss=False, icon_value=icon, expand=True)
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
        layout.template_list(ActionsUIList.bl_idname, "", obj, "actions", obj, "active")
        layout.separator()

        col = layout.column()
        row = col.row(align=True)
        row.enabled = False
        row.label(text="Final length")
        row.prop(obj, "animation_length", slider=False, text="")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator(ImportActionOperator.bl_idname, text='Import', icon="IMPORT")
        row.operator(DeleteItem.bl_idname, text='Delete', icon="REMOVE")
        row = col.row(align=True)
        row.operator(MoveItem.bl_idname, text='Up', icon="TRIA_UP").direction = 'UP'
        row.operator(MoveItem.bl_idname, text='Down', icon="TRIA_DOWN").direction = 'DOWN'

        sublayout = layout.box()
        if obj.active >= 0 and obj.actions:
            item = obj.actions[obj.active]
            col = sublayout.column(align=True)
            row = col.row()
            row.enabled = False
            row.prop(item, "path")

            row = col.row()
            row.prop(item, "name")

            item.length_group.draw(col)

        layout.separator()
        col = layout.column()
        if not obj.is_applied:
            col.label(text="Current actions were not applied yet!", icon="ERROR")
        row = col.row()
        row.operator(ApplyOperator.bl_idname, text="Apply", icon="WORKSPACE")
        row.operator(ExportSomeData.bl_idname, text="Export", icon="EXPORT")


class DeleteItem(Operator):
    """Deletes the selected action."""

    bl_idname = "my_list.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(cls, context):
        return context.object.data.actions

    def execute(self, context):
        my_list = context.object.data.actions
        index = context.object.data.active

        my_list.remove(index)
        context.object.data.active = min(max(0, index - 1), len(my_list) - 1)
        on_actions_update()
        return {'FINISHED'}


class MoveItem(Operator):
    """Moves the selected action up/down."""

    bl_idname = "my_list.move_item"
    bl_label = "Move an item in the list"

    direction: bpy.props.EnumProperty(items=(('UP', 'Up', ""),
                                             ('DOWN', 'Down', ""),))

    @classmethod
    def poll(cls, context):
        return context.object.data.actions

    def move_index(self, context):
        """ Move index of an item render queue while clamping it. """

        index = context.object.data.active
        list_length = len(context.object.data.actions) - 1  # (index starts at 0)
        new_index = index + (-1 if self.direction == 'UP' else 1)

        context.object.data.active = max(0, min(new_index, list_length))

    def execute(self, context):
        my_list = context.object.data.actions
        index = context.object.data.active

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        my_list.move(neighbor, index)
        self.move_index(context)

        return {'FINISHED'}
