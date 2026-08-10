"""Extract Orenburg municipal boundaries from the HSE municipality shapefile.

Usage:
    python scripts/extract_orenburg_boundaries.py input.shp output.geojson

The source dataset uses EPSG:3857. Output coordinates are converted to WGS84
and rounded to keep the browser payload compact.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import shapefile


EARTH_RADIUS = 6_378_137.0
REGION_NAME = "Оренбургская область"


def web_mercator_to_wgs84(point: list[float] | tuple[float, float]) -> list[float]:
    x, y = point
    longitude = math.degrees(x / EARTH_RADIUS)
    latitude = math.degrees(2 * math.atan(math.exp(y / EARTH_RADIUS)) - math.pi / 2)
    return [round(longitude, 5), round(latitude, 5)]


def transform_coordinates(value: Any) -> Any:
    if (
        isinstance(value, (list, tuple))
        and len(value) == 2
        and all(isinstance(item, (int, float)) for item in value)
    ):
        return web_mercator_to_wgs84(value)
    return [transform_coordinates(item) for item in value]


def extract(source: Path, destination: Path) -> None:
    reader = shapefile.Reader(str(source), encoding="utf-8")
    field_names = [field[0] for field in reader.fields[1:]]
    features: list[dict[str, Any]] = []

    for item in reader.iterShapeRecords():
        record = dict(zip(field_names, item.record))
        if record.get("region") != REGION_NAME:
            continue

        geometry = item.shape.__geo_interface__
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "oktmo": record.get("oktmo"),
                    "name": record.get("name"),
                    "type": record.get("type"),
                    "center": record.get("admcen"),
                },
                "geometry": {
                    "type": geometry["type"],
                    "coordinates": transform_coordinates(geometry["coordinates"]),
                },
            }
        )

    collection = {
        "type": "FeatureCollection",
        "name": "Муниципальные образования Оренбургской области",
        "source": "НИУ ВШЭ; геометрия OpenStreetMap; атрибуты Росстат; границы на 01.01.2021",
        "features": sorted(features, key=lambda feature: feature["properties"]["name"]),
    }

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(collection, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"Wrote {len(features)} features to {destination}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: extract_orenburg_boundaries.py input.shp output.geojson")
    extract(Path(sys.argv[1]), Path(sys.argv[2]))
