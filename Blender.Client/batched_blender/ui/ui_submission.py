﻿#-------------------------------------------------------------------------
#
# Batch Apps Blender Addon
#
# Copyright (c) Microsoft Corporation.  All rights reserved.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#--------------------------------------------------------------------------

import bpy


def static(ui, layout, active):
    """Display static job details reflecting global render settings.

    :param ui: The instance of the Interface panel class.
    :type ui: :class:`.Interface`
    :param layout: The layout object, used for creating and placing ui components.
    :type layout: :class:`bpy.types.UILayout`
    :param active: Whether UI components are enabled.
    :type active: bool
    """
    width = int(bpy.context.scene.render.resolution_x*\
        (bpy.context.scene.render.resolution_percentage/100))
    height = int(bpy.context.scene.render.resolution_y*\
        (bpy.context.scene.render.resolution_percentage/100))
    output = bpy.context.scene.batch_submission.image_format
    ui.label("Width: {0}".format(width), layout.row(), active=active)
    ui.label("Height: {0}".format(height), layout.row(), active=active)
    ui.label("Output: {0}".format(output), layout.row(), active=active)
    if bpy.context.scene.render.engine == 'LUXRENDER_RENDER':
        samples = bpy.context.scene.batch_submission.lux_samples
        ui.label("LuxRender halt samples: {0}".format(samples), layout.row(), active=active)

def variable(ui, layout, active):
    """Display frame selection controls.

    :param ui: The instance of the Interface panel class.
    :type ui: :class:`.Interface`
    :param layout: The layout object, used for creating and placing ui components.
    :type layout: :class:`bpy.types.UILayout`
    :param active: Whether UI components are enabled.
    :type active: bool
    """
    ui.prop(bpy.context.scene.batch_submission, "start_f", layout.row(),
            label="Start Frame ", active=active)
    ui.prop(bpy.context.scene.batch_submission, "end_f", layout.row(),
            label="End Frame ", active=active)
    if bpy.context.scene.render.engine == 'LUXRENDER_RENDER':
        ui.prop(bpy.context.scene.batch_submission, "lux_tasks_per_frame", layout.row(),
            label="Tasks Per Frame ", active=active)
    else:
        ui.prop(bpy.context.scene.batch_submission, "video_merge", layout.row(),
            label="Merge Frames to Video ", active=active)


def pool_select(ui, layout, active):
    """Display pool selection controls.

    :param ui: The instance of the Interface panel class.
    :type ui: :class:`.Interface`
    :param layout: The layout object, used for creating and placing ui components.
    :type layout: :class:`bpy.types.UILayout`
    :param active: Whether UI components are enabled.
    :type active: bool
    """
    ui.label("", layout)
    if bpy.context.scene.render.engine == 'LUXRENDER_RENDER':
        ui.prop(bpy.context.scene.batch_pools, "lux_app_image", layout.row(), "Application Package:", active=active)
        ui.prop(bpy.context.scene.batch_pools, "lux_app_version", layout.row(), "Application Version:", active=active)
    ui.prop(bpy.context.scene.batch_submission, "pool_type", layout.row(),
            label=None, expand=True, active=active)
    if bpy.context.scene.batch_submission.pool_type == {"reuse"}:
        ui.label("Use an existing persistant pool by ID", layout.row(), active=active)
        ui.prop(bpy.context.scene.batch_submission, "pool_id",
                layout.row(), active=active)
    elif bpy.context.scene.batch_submission.pool_type == {"create"}:
        ui.label("Create a new persistant pool", layout.row(), active=active)
        ui.prop(bpy.context.scene.batch_pools, "pool_name",
                layout.row(), "Name:", active=active)
        ui.prop(bpy.context.scene.batch_pools, "pool_size",
                layout.row(), "Number of nodes:", active=active)
    else:
        ui.label("Auto provision a pool for this job", layout.row(), active=active)
        ui.prop(bpy.context.scene.batch_pools, "pool_size",
                layout.row(), "Number of nodes:", active=active)

def pre_submission(ui, layout):
    """Display any warnings before job submission.

    :param ui: The instance of the Interface panel class.
    :type ui: :class:`.Interface`
    :param layout: The layout object, used for creating and placing ui components.
    :type layout: :class:`bpy.types.UILayout`
    """
    if not bpy.context.scene.batch_submission.valid_format:
        ui.label("Warning: Output format {0}".format(
            bpy.context.scene.render.image_settings.file_format), layout)
        ui.label("not supported. Using PNG instead", layout)
        row = layout.row(align=True)
        row.alert=True
        ui.operator("submission.start", "Submit Job", row)
    elif not bpy.context.scene.batch_submission.valid_range:
        ui.label("Warning: Selected frame range falls", layout)
        ui.label("outside global render range", layout)
        row = layout.row(align=True)
        row.alert=True
        ui.operator("submission.start", "Submit Job", row)
    elif bpy.context.scene.render.engine == 'LUXRENDER_RENDER' and bpy.data.scenes['Scene'].luxrender_halt.haltspp == 0:
        ui.label("Warning: Not halt sample value set.", layout)
        ui.label("Using default value {}".format(bpy.context.scene.batch_submission.lux_samples), layout)
        row = layout.row(align=True)
        row.alert=True
        ui.operator("submission.start", "Submit Job", row)
    else:
        ui.label("", layout)
        ui.label("", layout)
        ui.operator("submission.start", "Submit Job", layout)
    ui.operator("shared.home", "Return Home", layout)


def post_submission(ui, layout):
    """Display the job processing message.

    :param ui: The instance of the Interface panel class.
    :type ui: :class:`.Interface`
    :param layout: The layout object, used for creating and placing ui components.
    :type layout: :class:`bpy.types.UILayout`
    """
    ui.label("Submission now processing.", layout.row(align=True), "CENTER")
    ui.label("See console for progress.", layout.row(align=True), "CENTER")
    ui.label("Please don't close blender.", layout.row(align=True), "CENTER")


def submit(ui, layout):
    """Display new job submission page.

    :param ui: The instance of the Interface panel class.
    :type ui: :class:`.Interface`
    :param layout: The layout object, used for creating and placing ui components.
    :type layout: :class:`bpy.types.UILayout`
    """
    ui.prop(bpy.context.scene.batch_submission, "title", layout,
            label="Job name ", active=True)
    static(ui, layout, True)
    variable(ui, layout, True)
    pool_select(ui, layout, True)
    pre_submission(ui, layout)

def processing(ui, layout):
    """Display job submission processing page.

    :param ui: The instance of the Interface panel class.
    :type ui: :class:`.Interface`
    :param layout: The layout object, used for creating and placing ui components.
    :type layout: :class:`bpy.types.UILayout`
    """
    ui.prop(bpy.context.scene.batch_submission, "title", layout.row(),
            label="Job name ", active=False)
    static(ui, layout, False)
    variable(ui, layout, False)
    pool_select(ui, layout, False)
    post_submission(ui, layout)
    ui.label("", layout)


def submitted(ui, layout):
    """Display job submitted page.

    :param ui: The instance of the Interface panel class.
    :type ui: :class:`.Interface`
    :param layout: The layout object, used for creating and placing ui components.
    :type layout: :class:`bpy.types.UILayout`
    """
    sublayout = layout.box()
    ui.label("Submission Successfull!", sublayout.row(align=True), "CENTER")
    ui.label("", sublayout, "CENTER")
    ui.operator("shared.home", "Return Home", layout)