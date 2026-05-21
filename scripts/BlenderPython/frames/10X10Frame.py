import bpy

# =====================================================
# 10x10 GESSO PANEL FRAME — UNIVERSAL QUARTER CORNER
#
# Print this ONE L-shaped corner piece 4 times.
# Rotate each copy to form the full frame.
#
# This is the best version for Bambu bed limits.
#
# Matches the working 6x6 frame logic:
# - 0.08" outside wall
# - 0.12" support ledge
# - 0.115" pocket depth
# - 0.50" total standoff
#
# Geometry is built in millimeters for Bambu/STL correctness.
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
# SAME AS WORKING 6x6 FRAME
# -------------------------

clearance_in = 0.02
wall_in = 0.08
pocket_depth_in = 0.115
total_depth_in = 0.50
ledge_width_in = 0.12
bevel_in = 0.01

# Slight overlap where boxes meet so slicer treats it as solid
overlap_mm = 0.30

# -------------------------
# CONVERT TO MM
# -------------------------

panel_w = panel_w_in * INCH_TO_MM
panel_h = panel_h_in * INCH_TO_MM
panel_thick = panel_thick_in * INCH_TO_MM

clearance = clearance_in * INCH_TO_MM
wall = wall_in * INCH_TO_MM
pocket_depth = pocket_depth_in * INCH_TO_MM
total_depth = total_depth_in * INCH_TO_MM
ledge_width = ledge_width_in * INCH_TO_MM
bevel_amount = bevel_in * INCH_TO_MM

# -------------------------
# DERIVED DIMENSIONS
# -------------------------

inner_w = panel_w + clearance
inner_h = panel_h + clearance

outer_w = inner_w + wall * 2
outer_h = inner_h + wall * 2

ledge_z = total_depth - pocket_depth
panel_proud_in = panel_thick_in - pocket_depth_in

# Each corner piece reaches halfway along each side
half_outer_w = outer_w / 2
half_outer_h = outer_h / 2
half_inner_w = inner_w / 2
half_inner_h = inner_h / 2

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
# HELPERS
# -------------------------

def add_box(name, size_x, size_y, size_z, loc_x, loc_y, loc_z):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(loc_x, loc_y, loc_z))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = (size_x, size_y, size_z)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj

def join_objects(name, objs):
    bpy.ops.object.select_all(action='DESELECT')

    for obj in objs:
        obj.select_set(True)

    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()

    joined = bpy.context.object
    joined.name = name

    bevel = joined.modifiers.new("Tiny_Print_Bevel", "BEVEL")
    bevel.width = bevel_amount
    bevel.segments = 1

    weighted = joined.modifiers.new("Weighted_Normals", "WEIGHTED_NORMAL")

    bpy.context.view_layer.objects.active = joined
    joined.select_set(True)

    bpy.ops.object.modifier_apply(modifier=bevel.name)
    bpy.ops.object.modifier_apply(modifier=weighted.name)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    return joined

# =====================================================
# BUILD ONE UNIVERSAL CORNER PIECE
#
# This creates the TOP-RIGHT corner.
# Print 4 copies and rotate them for all corners.
# =====================================================

objects = []

# -------------------------
# HORIZONTAL OUTER WALL LEG
# top side, from center to right corner
# -------------------------

objects.append(add_box(
    "horizontal_outer_wall_leg",
    half_outer_w + overlap_mm,
    wall,
    total_depth,
    half_outer_w / 2 - overlap_mm / 2,
    half_outer_h - wall / 2,
    total_depth / 2
))

# -------------------------
# VERTICAL OUTER WALL LEG
# right side, from center to top corner
# -------------------------

objects.append(add_box(
    "vertical_outer_wall_leg",
    wall,
    half_outer_h + overlap_mm,
    total_depth,
    half_outer_w - wall / 2,
    half_outer_h / 2 - overlap_mm / 2,
    total_depth / 2
))

# -------------------------
# HORIZONTAL SUPPORT LEDGE
# inside top side
# -------------------------

objects.append(add_box(
    "horizontal_support_ledge",
    half_inner_w + overlap_mm,
    ledge_width,
    ledge_z,
    half_inner_w / 2 - overlap_mm / 2,
    half_inner_h - ledge_width / 2,
    ledge_z / 2
))

# -------------------------
# VERTICAL SUPPORT LEDGE
# inside right side
# -------------------------

objects.append(add_box(
    "vertical_support_ledge",
    ledge_width,
    half_inner_h + overlap_mm,
    ledge_z,
    half_inner_w - ledge_width / 2,
    half_inner_h / 2 - overlap_mm / 2,
    ledge_z / 2
))

# -------------------------
# JOIN INTO ONE PRINTABLE CORNER
# -------------------------

corner = join_objects(
    "PRINT_4X_10x10_UNIVERSAL_CORNER_FRAME_PIECE",
    objects
)

# Center object more nicely around origin
corner.location.x = -half_outer_w / 2
corner.location.y = -half_outer_h / 2
corner.location.z = 0

# -------------------------
# REPORT
# -------------------------

print("10x10 UNIVERSAL CORNER FRAME PIECE CREATED")
print("")
print("PRINT THIS OBJECT 4 TIMES.")
print("Rotate each copy to create the four corners.")
print("")
print("MATCHES 6x6 FRAME SETTINGS:")
print(f"Wall thickness: {wall_in:.3f}\"")
print(f"Ledge width: {ledge_width_in:.3f}\"")
print(f"Pocket depth: {pocket_depth_in:.3f}\"")
print(f"Total standoff depth: {total_depth_in:.3f}\"")
print(f"Panel sits proud by: {panel_proud_in:.3f}\"")
print("")
print("ASSEMBLED FRAME:")
print(f"Outer assembled size: {outer_w:.2f} mm x {outer_h:.2f} mm")
print(f"Outer assembled size: {outer_w / 25.4:.3f}\" x {outer_h / 25.4:.3f}\"")
print(f"Panel pocket: {inner_w / 25.4:.3f}\" x {inner_h / 25.4:.3f}\"")
print("")
print("SINGLE CORNER PIECE APPROX SIZE:")
print(f"Width: {half_outer_w:.2f} mm")
print(f"Height: {half_outer_h:.2f} mm")
print(f"Depth: {total_depth:.2f} mm")
print("")
print("BAMBU CHECK:")
print("Each corner should be about 129.29 mm x 129.29 mm x 12.70 mm.")
