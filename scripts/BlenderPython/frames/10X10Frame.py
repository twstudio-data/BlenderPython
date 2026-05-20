import bpy

# =====================================================
# UNIVERSAL MITER RAIL FOR 10" GESSO PANEL FRAME
# Print this ONE rail 4 times.
#
# Input values are inches.
# Geometry is built in millimeters for Bambu/STL correctness.
#
# Design:
# - 45-degree mitered ends
# - Full-height outer wall
# - Internal ledge for 1/8" gesso panel
# - Open center once assembled
# - Panel sits slightly proud
# =====================================================

INCH_TO_MM = 25.4

# -------------------------
# PANEL SETTINGS — inches
# -------------------------

panel_size_in = 10.0
panel_thick_in = 0.125   # 1/8" gesso panel

# -------------------------
# FRAME SETTINGS — inches
# -------------------------

clearance_in = 0.02      # total clearance around panel
wall_in = 0.08           # outside vertical wall thickness
ledge_width_in = 0.12    # support ledge width
ledge_thickness_in = 0.08

pocket_depth_in = 0.115  # panel sits 0.010" proud
total_depth_in = 0.50    # wall standoff / side height

bevel_in = 0.01
overlap_mm = 0.25        # slight overlap so slicer unions ledge + wall cleanly

# -------------------------
# CONVERT TO MM
# -------------------------

panel_size = panel_size_in * INCH_TO_MM
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

inner_size = panel_size + clearance

# Outer assembled frame size
outer_size = inner_size + wall * 2

# Full rail length is the outer side length.
# With 45-degree miters, print 4 identical rails.
rail_length = outer_size

# Rail width from outside edge to inside ledge edge
rail_width = wall + ledge_width

ledge_top_z = total_depth - pocket_depth
ledge_bottom_z = ledge_top_z - ledge_thickness

panel_proud_in = panel_thick_in - pocket_depth_in

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
# MESH HELPERS
# -------------------------

def band_polygon(y0, y1):
    """
    Creates a 45-degree mitered strip band from y0 to y1.
    Rail runs along X.
    Outside edge is y=0.
    Inside direction is positive Y.

    45-degree miter logic:
    left edge shifts inward by y
    right edge shifts inward by y
    """
    L = rail_length

    x_left_y0 = -L / 2 + y0
    x_right_y0 = L / 2 - y0

    x_left_y1 = -L / 2 + y1
    x_right_y1 = L / 2 - y1

    return [
        (x_left_y0,  y0),
        (x_right_y0, y0),
        (x_right_y1, y1),
        (x_left_y1,  y1),
    ]

def create_prism(name, poly2d, z0, z1):
    """
    Creates a solid prism from a 2D polygon between z0 and z1.
    """
    verts = []

    # bottom verts
    for x, y in poly2d:
        verts.append((x, y, z0))

    # top verts
    for x, y in poly2d:
        verts.append((x, y, z1))

    faces = []

    # bottom face
    faces.append((0, 3, 2, 1))

    # top face
    faces.append((4, 5, 6, 7))

    # side faces
    faces.append((0, 1, 5, 4))
    faces.append((1, 2, 6, 5))
    faces.append((2, 3, 7, 6))
    faces.append((3, 0, 4, 7))

    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    return obj

# -------------------------
# CREATE THE UNIVERSAL RAIL
# -------------------------

objects = []

# Full-height outside wall band
outer_wall_poly = band_polygon(0, wall)
outer_wall = create_prism(
    "Rail_Full_Height_Outer_Wall",
    outer_wall_poly,
    0,
    total_depth
)
objects.append(outer_wall)

# Support ledge band
# It starts slightly inside/overlapping the wall and extends inward.
ledge_y0 = wall - overlap_mm
ledge_y1 = wall + ledge_width

ledge_poly = band_polygon(ledge_y0, ledge_y1)
ledge = create_prism(
    "Rail_Internal_Support_Ledge",
    ledge_poly,
    ledge_bottom_z,
    ledge_top_z
)
objects.append(ledge)

# -------------------------
# JOIN INTO ONE OBJECT
# -------------------------

bpy.ops.object.select_all(action='DESELECT')

for obj in objects:
    obj.select_set(True)

bpy.context.view_layer.objects.active = objects[0]
bpy.ops.object.join()

rail = bpy.context.object
rail.name = "PRINT_4X_Universal_10x10_Miter_Rail"

# -------------------------
# BEVEL FOR PRINTABILITY
# -------------------------

bevel = rail.modifiers.new("Tiny_Print_Bevel", "BEVEL")
bevel.width = bevel_amount
bevel.segments = 1

weighted = rail.modifiers.new("Weighted_Normals", "WEIGHTED_NORMAL")

bpy.context.view_layer.objects.active = rail
rail.select_set(True)

bpy.ops.object.modifier_apply(modifier=bevel.name)
bpy.ops.object.modifier_apply(modifier=weighted.name)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Move object so it sits centered nicely on origin
rail.location = (0, -rail_width / 2, 0)

# -------------------------
# REPORT
# -------------------------

print("UNIVERSAL 10x10 MITER RAIL CREATED")
print("")
print("PRINT THIS OBJECT 4 TIMES.")
print("")
print("ASSEMBLED FRAME:")
print(f"Outer assembled size: {outer_size:.2f} mm x {outer_size:.2f} mm")
print(f"Outer assembled size: {outer_size / 25.4:.3f}\" x {outer_size / 25.4:.3f}\"")
print(f"Inner panel pocket: {inner_size / 25.4:.3f}\" x {inner_size / 25.4:.3f}\"")
print("")
print("SINGLE RAIL:")
print(f"Rail length: {rail_length:.2f} mm")
print(f"Rail length: {rail_length / 25.4:.3f}\"")
print(f"Rail width: {rail_width:.2f} mm")
print(f"Rail width: {rail_width / 25.4:.3f}\"")
print(f"Rail depth / wall standoff: {total_depth / 25.4:.3f}\"")
print("")
print("PANEL FIT:")
print(f"Panel thickness: {panel_thick_in:.3f}\"")
print(f"Pocket depth: {pocket_depth_in:.3f}\"")
print(f"Panel sits proud by: {panel_proud_in:.3f}\"")
print("")
print("PRINT NOTE:")
print("The rail is slightly longer than a Bambu 256 mm bed,")
print("so rotate it diagonally on the plate.")
