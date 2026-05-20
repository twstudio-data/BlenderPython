import bpy

# =====================================================
# BAMBU-SAFE OPEN FRAME FOR 10" GESSO PANEL
# Builds from solid rectangular rails so slicer does NOT fill the center.
# Input values are inches, geometry is built in millimeters.
# =====================================================

INCH_TO_MM = 25.4

# -------------------------
# PANEL SETTINGS — inches
# -------------------------

panel_w_in = 10.0
panel_h_in = 10.0
panel_thick_in = 0.125

# -------------------------
# FRAME SETTINGS — inches
# -------------------------

clearance_in = 0.02

wall_in = 0.08              # outside wall thickness
ledge_width_in = 0.12       # shelf holding panel
ledge_thickness_in = 0.08   # actual thickness of ledge material

pocket_depth_in = 0.115     # panel sits 0.010" proud
total_depth_in = 0.50       # serious wall standoff

bevel_in = 0.01

# -------------------------
# CONVERT TO MM
# -------------------------

panel_w = panel_w_in * INCH_TO_MM
panel_h = panel_h_in * INCH_TO_MM
panel_thick = panel_thick_in * INCH_TO_MM

clearance = clearance_in * INCH_TO_MM
wall = wall_in * INCH_TO_MM
ledge_width = ledge_width_in * INCH_TO_MM
ledge_thickness = ledge_thickness_in * INCH_TO_MM

pocket_depth = pocket_depth_in * INCH_TO_MM
total_depth = total_depth_in * INCH_TO_MM
bevel_amount = bevel_in * INCH_TO_MM

# -------------------------
# DERIVED DIMENSIONS
# -------------------------

inner_w = panel_w + clearance
inner_h = panel_h + clearance

outer_w = inner_w + wall * 2
outer_h = inner_h + wall * 2

# ledge sits below the top, creating the pocket
ledge_top_z = total_depth - pocket_depth
ledge_bottom_z = ledge_top_z - ledge_thickness

# opening underneath ledge
support_opening_w = inner_w - ledge_width * 2
support_opening_h = inner_h - ledge_width * 2

# -------------------------
# CLEAN SCENE
# -------------------------

if bpy.ops.object.mode_set.poll():
    bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.length_unit = 'MILLIMETERS'
bpy.context.scene.unit_settings.scale_length = 1.0

# -------------------------
# CREATE BOX HELPER
# -------------------------

def add_box(name, size_x, size_y, size_z, loc_x, loc_y, loc_z):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(loc_x, loc_y, loc_z))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = (size_x, size_y, size_z)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj

objects = []

# =====================================================
# OUTER FRAME: four full-height rails
# =====================================================

# left rail
objects.append(add_box(
    "Outer_Left_Rail",
    wall,
    outer_h,
    total_depth,
    -outer_w / 2 + wall / 2,
    0,
    total_depth / 2
))

# right rail
objects.append(add_box(
    "Outer_Right_Rail",
    wall,
    outer_h,
    total_depth,
    outer_w / 2 - wall / 2,
    0,
    total_depth / 2
))

# bottom rail
objects.append(add_box(
    "Outer_Bottom_Rail",
    outer_w,
    wall,
    total_depth,
    0,
    -outer_h / 2 + wall / 2,
    total_depth / 2
))

# top rail
objects.append(add_box(
    "Outer_Top_Rail",
    outer_w,
    wall,
    total_depth,
    0,
    outer_h / 2 - wall / 2,
    total_depth / 2
))

# =====================================================
# INTERNAL LEDGE: four thinner support rails
# These hold the gesso panel but leave the middle open.
# =====================================================

ledge_z_center = ledge_bottom_z + ledge_thickness / 2

# left ledge
objects.append(add_box(
    "Ledge_Left",
    ledge_width,
    inner_h,
    ledge_thickness,
    -inner_w / 2 + ledge_width / 2,
    0,
    ledge_z_center
))

# right ledge
objects.append(add_box(
    "Ledge_Right",
    ledge_width,
    inner_h,
    ledge_thickness,
    inner_w / 2 - ledge_width / 2,
    0,
    ledge_z_center
))

# bottom ledge
objects.append(add_box(
    "Ledge_Bottom",
    support_opening_w,
    ledge_width,
    ledge_thickness,
    0,
    -inner_h / 2 + ledge_width / 2,
    ledge_z_center
))

# top ledge
objects.append(add_box(
    "Ledge_Top",
    support_opening_w,
    ledge_width,
    ledge_thickness,
    0,
    inner_h / 2 - ledge_width / 2,
    ledge_z_center
))

# -------------------------
# JOIN INTO ONE OBJECT
# -------------------------

bpy.ops.object.select_all(action='DESELECT')

for obj in objects:
    obj.select_set(True)

bpy.context.view_layer.objects.active = objects[0]
bpy.ops.object.join()

frame = bpy.context.object
frame.name = "Bambu_Safe_Open_Gesso_Frame_10x10"

# -------------------------
# BEVEL FOR PRINTABILITY
# -------------------------

bevel = frame.modifiers.new("Tiny_Print_Bevel", "BEVEL")
bevel.width = bevel_amount
bevel.segments = 1

weighted = frame.modifiers.new("Weighted_Normals", "WEIGHTED_NORMAL")

# Apply modifiers so STL is clean
bpy.context.view_layer.objects.active = frame
frame.select_set(True)

bpy.ops.object.modifier_apply(modifier=bevel.name)
bpy.ops.object.modifier_apply(modifier=weighted.name)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# -------------------------
# REPORT
# -------------------------

panel_proud_in = panel_thick_in - pocket_depth_in

print("BAMBU-SAFE OPEN FRAME CREATED (10x10)")
print(f"Outer size: {outer_w:.2f} mm x {outer_h:.2f} mm")
print(f"Outer size: {outer_w / 25.4:.3f}\" x {outer_h / 25.4:.3f}\"")
print(f"Total depth: {total_depth / 25.4:.3f}\"")
print(f"Panel pocket: {inner_w / 25.4:.3f}\" x {inner_h / 25.4:.3f}\"")
print(f"Wall thickness: {wall_in:.3f}\"")
print(f"Ledge width: {ledge_width_in:.3f}\"")
print(f"Ledge thickness: {ledge_thickness_in:.3f}\"")
print(f"Pocket depth: {pocket_depth_in:.3f}\"")
print(f"Panel sits proud by: {panel_proud_in:.3f}\"")
print(f"Open center underneath: {support_opening_w / 25.4:.3f}\" x {support_opening_h / 25.4:.3f}\"")
