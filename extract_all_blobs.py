"""
Extract morphing blob shapes for all 7 high-change areas.
Same pipeline as notebook cell 19 (Fernvale), extended to all 7 areas.
Outputs scroll_shapes_all.js with CSS-animation-ready SVG path data.

Uses FULL GRC/SMC boundaries (no viewport clipping).
A unified bounding box is computed from all 5 boundaries per area.
"""
import geopandas as gpd
import numpy as np
from shapely.geometry import box, Polygon, MultiPolygon, Point, mapping, shape
from shapely.ops import unary_union
import json
import os
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = "/Users/wongpeiting/Desktop/CU/python-work/electoral-boundaries"

# ── Load boundaries (same as notebook cells 2-3) ──
FILES = {
    2006: os.path.join(BASE_DIR, "ElectoralBoundary2006GEOJSON.geojson"),
    2011: os.path.join(BASE_DIR, "ElectoralBoundary2011GEOJSON.geojson"),
    2015: os.path.join(BASE_DIR, "ElectoralBoundary2015GEOJSON.geojson"),
    2020: os.path.join(BASE_DIR, "ElectoralBoundary2020GEOJSON.geojson"),
    2025: os.path.join(BASE_DIR, "ElectoralBoundary2025GEOJSON.geojson"),
}

print("Loading boundaries...")
raw_boundaries = {}
for year, filepath in FILES.items():
    gdf = gpd.read_file(filepath)
    gdf['geometry'] = gdf['geometry'].buffer(0)
    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=4326)
    if 'ED_DESC' in gdf.columns:
        gdf['district'] = gdf['ED_DESC'].str.upper().str.strip()
    elif 'Name' in gdf.columns:
        gdf['district'] = gdf['Name'].str.upper().str.strip()
    gdf['district'] = gdf['district'].str.replace(r'\s*-\s*', '-', regex=True)
    gdf['district'] = gdf['district'].str.replace(r'\s+', ' ', regex=True)
    raw_boundaries[year] = gdf
    print(f"  {year}: {len(gdf)} districts")

# Clip to 2025 land mask
land_mask = raw_boundaries[2025].geometry.unary_union.buffer(0)
boundaries = {}
for year, gdf in raw_boundaries.items():
    gdf = gdf.copy()
    gdf['geometry'] = gdf.geometry.intersection(land_mask)
    gdf = gdf[~gdf.geometry.is_empty].copy()
    gdf['geometry'] = gdf['geometry'].buffer(0)
    boundaries[year] = gdf

print("Boundaries loaded and clipped.\n")

# ── The 7 areas ──
AREAS = [
    {
        "id": "pioneer",
        "label": "Pioneer / Nanyang",
        "center": (103.68, 1.35),
        "districts": {
            2006: "HONG KAH",
            2011: "CHUA CHU KANG",
            2015: "CHUA CHU KANG",
            2020: "WEST COAST",
            2025: "WEST COAST-JURONG WEST",
        },
        "labels": {
            2006: "Hong Kah GRC",
            2011: "Chua Chu Kang GRC",
            2015: "Chua Chu Kang GRC",
            2020: "West Coast GRC",
            2025: "West Coast-Jurong West GRC",
        },
    },
    {
        "id": "springleaf",
        "label": "Yishun East",
        "center": (103.854, 1.431),
        "districts": {
            2006: "NEE SOON EAST",
            2011: "NEE SOON",
            2015: "SEMBAWANG",
            2020: "NEE SOON",
            2025: "NEE SOON",
        },
        "labels": {
            2006: "Nee Soon East SMC",
            2011: "Nee Soon GRC",
            2015: "Sembawang GRC",
            2020: "Nee Soon GRC",
            2025: "Nee Soon GRC",
        },
    },
    {
        "id": "bendemeer",
        "label": "Bendemeer / Boon Keng",
        "center": (103.842, 1.329),
        "districts": {
            2006: "TANJONG PAGAR",
            2011: "MOULMEIN-KALLANG",
            2015: "BISHAN-TOA PAYOH",
            2020: "JALAN BESAR",
            2025: "JALAN BESAR",
        },
        "labels": {
            2006: "Tanjong Pagar GRC",
            2011: "Moulmein-Kallang GRC",
            2015: "Bishan-Toa Payoh GRC",
            2020: "Jalan Besar GRC",
            2025: "Jalan Besar GRC",
        },
    },
    {
        "id": "geylang",
        "label": "Geylang East / Circuit Rd",
        "center": (103.885, 1.327),
        "districts": {
            2006: "MACPHERSON",
            2011: "MARINE PARADE",
            2015: "MACPHERSON",
            2020: "MACPHERSON",
            2025: "MARINE PARADE-BRADDELL HEIGHTS",
        },
        "labels": {
            2006: "MacPherson SMC",
            2011: "Marine Parade GRC",
            2015: "MacPherson SMC",
            2020: "MacPherson SMC",
            2025: "Marine Parade-Braddell Heights GRC",
        },
    },
    {
        "id": "fernvale",
        "label": "Fernvale",
        "center": (103.881, 1.396),
        "districts": {
            2006: "ANG MO KIO",
            2011: "SENGKANG WEST",
            2015: "SENGKANG WEST",
            2020: "ANG MO KIO",
            2025: "JALAN KAYU",
        },
        "labels": {
            2006: "Ang Mo Kio GRC",
            2011: "Sengkang West SMC",
            2015: "Sengkang West SMC",
            2020: "Ang Mo Kio GRC",
            2025: "Jalan Kayu SMC",
        },
    },
    {
        "id": "siglap",
        "label": "Siglap / Frankel",
        "center": (103.93, 1.317),
        "districts": {
            2006: "EAST COAST",
            2011: "JOO CHIAT",
            2015: "MARINE PARADE",
            2020: "MARINE PARADE",
            2025: "EAST COAST",
        },
        "labels": {
            2006: "East Coast GRC",
            2011: "Joo Chiat SMC",
            2015: "Marine Parade GRC",
            2020: "Marine Parade GRC",
            2025: "East Coast GRC",
        },
    },
    {
        "id": "tohguan",
        "label": "Toh Guan",
        "center": (103.758, 1.320),
        "districts": {
            2006: "HOLLAND-BUKIT TIMAH",
            2011: "WEST COAST",
            2015: "JURONG",
            2020: "JURONG",
            2025: "JURONG EAST-BUKIT BATOK",
        },
        "labels": {
            2006: "Holland-Bukit Timah GRC",
            2011: "West Coast GRC",
            2015: "Jurong GRC",
            2020: "Jurong GRC",
            2025: "Jurong East-Bukit Batok GRC",
        },
    },
]

# ── Pipeline parameters ──
BOUNDS_PAD_FRAC = 0.05  # 5% padding on each side of unified bounding box
NUM_VERTICES = 150
SVG_W, SVG_H = 800, 600
BUFFER_MERGE = 0.003  # buffer to merge narrow inlets


def resample_polygon(poly, n):
    """Resample polygon boundary to exactly n evenly-spaced vertices."""
    ring = poly.exterior
    total_length = ring.length
    points = []
    for i in range(n):
        d = (i / n) * total_length
        pt = ring.interpolate(d)
        points.append((pt.x, pt.y))
    return points


def rotate_to_north(coords, center):
    """Rotate coordinate list so the start point is nearest to due north of center."""
    north = (center[0], center[1] + 1)
    min_dist = float('inf')
    min_idx = 0
    for i, (x, y) in enumerate(coords):
        d = (x - north[0])**2 + (y - north[1])**2
        if d < min_dist:
            min_dist = d
            min_idx = i
    return coords[min_idx:] + coords[:min_idx]


def geo_to_svg(coords, bounds):
    """Convert (lon, lat) list to SVG (x, y) within 800x600 viewBox.
    bounds = (lon_min, lat_min, lon_max, lat_max).
    Maintains aspect ratio, centered in viewBox."""
    lon_min, lat_min, lon_max, lat_max = bounds
    geo_w = lon_max - lon_min
    geo_h = lat_max - lat_min

    scale_x = SVG_W / geo_w if geo_w > 0 else 1
    scale_y = SVG_H / geo_h if geo_h > 0 else 1
    scale = min(scale_x, scale_y)

    used_w = geo_w * scale
    used_h = geo_h * scale
    off_x = (SVG_W - used_w) / 2
    off_y = (SVG_H - used_h) / 2

    svg_coords = []
    for lon, lat in coords:
        x = (lon - lon_min) * scale + off_x
        y = (lat_max - lat) * scale + off_y
        svg_coords.append([round(x, 1), round(y, 1)])
    return svg_coords


def coords_to_path(svg_coords):
    """Convert [[x,y],...] to SVG path string."""
    return 'M' + 'L'.join(f'{p[0]},{p[1]}' for p in svg_coords) + 'Z'


def best_poly(geoms, center_pt):
    """Prefer the polygon containing the centre point, else largest."""
    for g in geoms:
        if g.geom_type == 'MultiPolygon':
            for sub in g.geoms:
                if sub.contains(center_pt):
                    return sub
        elif g.contains(center_pt):
            return g
    return max(geoms, key=lambda g: g.area)


# ── Process each area ──
all_areas = []
area_bounds = {}  # store per-area bounds for core extraction

for area in AREAS:
    area_id = area["id"]
    center = area["center"]
    label = area["label"]
    center_pt = Point(center)
    print(f"Processing: {label} ({area_id})")

    # ── Pass 1: collect all 5 full GRC geometries (no viewport clipping) ──
    raw_geoms = {}
    for year in [2006, 2011, 2015, 2020, 2025]:
        expected_name = area["districts"][year]
        gdf = boundaries[year]
        match = gdf[gdf['district'].str.contains(expected_name, case=False, na=False)]

        if len(match) == 0:
            print(f"  WARNING: {expected_name} not found in {year}")
            continue

        geom = match.iloc[0].geometry

        # Buffer/unbuffer first to merge land-mask clipping artifacts
        geom = geom.buffer(BUFFER_MERGE).buffer(-BUFFER_MERGE)
        if geom.is_empty:
            print(f"  WARNING: Buffer collapsed geometry for {year}")
            continue

        # Pick main body (largest polygon) — avoids tiny clipping fragments
        if geom.geom_type == 'MultiPolygon':
            geom = max(geom.geoms, key=lambda g: g.area)
        elif geom.geom_type == 'GeometryCollection':
            polys = [g for g in geom.geoms if g.geom_type in ('Polygon', 'MultiPolygon')]
            if polys:
                geom = max(polys, key=lambda g: g.area)
            else:
                print(f"  WARNING: No polygon in GeometryCollection for {year}")
                continue

        raw_geoms[year] = geom

    if not raw_geoms:
        print(f"  SKIPPED: no valid geometries")
        continue

    # ── Compute unified bounding box from all 5 shapes + padding ──
    all_union = unary_union(list(raw_geoms.values()))
    bx_min, by_min, bx_max, by_max = all_union.bounds
    bw = bx_max - bx_min
    bh = by_max - by_min
    pad_x = bw * BOUNDS_PAD_FRAC
    pad_y = bh * BOUNDS_PAD_FRAC
    bounds = (bx_min - pad_x, by_min - pad_y, bx_max + pad_x, by_max + pad_y)
    area_bounds[area_id] = bounds
    print(f"  Unified bounds: lon [{bounds[0]:.4f}, {bounds[2]:.4f}], lat [{bounds[1]:.4f}, {bounds[3]:.4f}]")

    # ── Pass 2: process each geometry into SVG paths ──
    shapes = []
    for year in [2006, 2011, 2015, 2020, 2025]:
        if year not in raw_geoms:
            continue

        geom = raw_geoms[year]

        # Resample to fixed vertex count (buffer/unbuffer already done in Pass 1)
        pts = resample_polygon(geom, NUM_VERTICES)
        pts = rotate_to_north(pts, center)

        # Project to SVG coords using unified bounds
        svg_coords = geo_to_svg(pts, bounds)
        path_d = coords_to_path(svg_coords)

        shapes.append({
            "year": year,
            "name": area["labels"][year],
            "path": path_d,
            "coords": svg_coords,
        })

        print(f"  {year}: {area['labels'][year]} -> {len(pts)} vertices")

    # Center dot in SVG
    center_svg = geo_to_svg([center], bounds)[0]

    area_data = {
        "id": area_id,
        "label": label,
        "center": center_svg,
        "shapes": shapes,
    }
    all_areas.append(area_data)
    print()

# ── Extract core polygons for ALL 7 areas ──
print("Extracting core polygons from boundary_changes_final.geojson...")
with open(os.path.join(BASE_DIR, 'boundary_changes_final.geojson')) as f:
    final_data = json.load(f)

# Each area's core = union of features whose 5-year history matches the area's history
core_histories = {
    "pioneer":    ['HONG KAH', 'CHUA CHU KANG', 'CHUA CHU KANG', 'WEST COAST', 'WEST COAST-JURONG WEST'],
    "springleaf": ['NEE SOON EAST', 'NEE SOON', 'SEMBAWANG', 'NEE SOON', 'NEE SOON'],
    "bendemeer":  ['TANJONG PAGAR', 'MOULMEIN-KALLANG', 'BISHAN-TOA PAYOH', 'JALAN BESAR', 'JALAN BESAR'],
    "geylang":    ['MACPHERSON', 'MARINE PARADE', 'MACPHERSON', 'MACPHERSON', 'MARINE PARADE-BRADDELL HEIGHTS'],
    "fernvale":   ['ANG MO KIO', 'SENGKANG WEST', 'SENGKANG WEST', 'ANG MO KIO', 'JALAN KAYU'],
    "siglap":     ['EAST COAST', 'JOO CHIAT', 'MARINE PARADE', 'MARINE PARADE', 'EAST COAST'],
    "tohguan":    ['HOLLAND-BUKIT TIMAH', 'WEST COAST', 'JURONG', 'JURONG', 'JURONG EAST-BUKIT BATOK'],
}

core_paths = {}
for area_data in all_areas:
    area_id = area_data["id"]
    center = [a for a in AREAS if a["id"] == area_id][0]["center"]
    bounds = area_bounds[area_id]
    target_h = core_histories[area_id]

    # Find matching features
    matches = [f for f in final_data['features'] if f['properties']['h'] == target_h]
    print(f"  {area_id}: {len(matches)} features with history {target_h[:2]}...{target_h[-1]}")

    if not matches:
        core_paths[area_id] = ""
        continue

    # Union all matching features (buffer(0) fixes invalid geometries)
    polys = [shape(f['geometry']).buffer(0) for f in matches]
    core_union = unary_union(polys).buffer(0)

    if core_union.is_empty:
        print(f"    WARNING: core polygon empty")
        core_paths[area_id] = ""
        continue

    # Take largest polygon if multi
    if core_union.geom_type == 'MultiPolygon':
        core_union = max(core_union.geoms, key=lambda g: g.area)
    elif core_union.geom_type == 'GeometryCollection':
        poly_parts = [g for g in core_union.geoms if g.geom_type in ('Polygon', 'MultiPolygon')]
        if poly_parts:
            core_union = max(poly_parts, key=lambda g: g.area)
        else:
            core_paths[area_id] = ""
            continue

    # Project core using same per-area bounds (no viewport clipping)
    core_coords = list(core_union.exterior.coords)
    core_svg = geo_to_svg(core_coords, bounds)
    core_paths[area_id] = coords_to_path(core_svg)
    print(f"    -> {len(core_coords)} vertices, path len={len(core_paths[area_id])}")

# ── Export ──
export_data = {
    "areas": [],
}

for area_data in all_areas:
    export_area = {
        "id": area_data["id"],
        "label": area_data["label"],
        "center": area_data["center"],
        "corePath": core_paths.get(area_data["id"], ""),
        "shapes": [],
    }
    for s in area_data["shapes"]:
        export_area["shapes"].append({
            "year": s["year"],
            "name": s["name"],
            "path": s["path"],
        })
    export_data["areas"].append(export_area)

export_path = os.path.join(BASE_DIR, 'scroll_shapes_all.js')
with open(export_path, 'w') as f:
    f.write('const blobData = ')
    json.dump(export_data, f)
    f.write(';\n')

file_size = os.path.getsize(export_path)
print(f"\nExported to scroll_shapes_all.js ({file_size / 1024:.1f} KB)")
print(f"Areas: {len(export_data['areas'])}")
for a in export_data['areas']:
    has_core = "with core" if a['corePath'] else "NO core"
    print(f"  {a['id']}: {a['label']} ({len(a['shapes'])} shapes, {has_core})")
