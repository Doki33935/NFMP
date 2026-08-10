#!/usr/bin/env python3
"""Emit SQL that places NFMP load-test fires inside Orenburg municipalities."""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path
from typing import Any


MUNICIPALITIES: dict[int, tuple[str, str]] = {
    1: ("г. Абдулино", "Абдулинский"),
    2: ("г. Бугуруслан", "город Бугуруслан"),
    3: ("г. Бузулук", "город Бузулук"),
    4: ("г. Гай", "Гайский"),
    5: ("г. Кувандык", "Кувандыкский"),
    6: ("г. Медногорск", "город Медногорск"),
    7: ("г. Новотроицк", "город Новотроицк"),
    8: ("г. Оренбург", "город Оренбург"),
    9: ("г. Орск", "город Орск"),
    10: ("г. Соль-Илецк", "Соль-Илецкий"),
    11: ("г. Сорочинск", "Сорочинский"),
    12: ("г. Ясный", "Ясненский"),
    13: ("ЗАТО Комаровский", "ЗАТО поселок Комаровский"),
    14: ("Абдулинский МО", "Абдулинский"),
    15: ("Адамовский район", "Адамовский муниципальный район"),
    16: ("Акбулакский район", "Акбулакский муниципальный район"),
    17: ("Александровский район", "Александровский муниципальный район"),
    18: ("Асекеевский район", "Асекеевский муниципальный район"),
    19: ("Беляевский район", "Беляевский муниципальный район"),
    20: ("Бугурусланский район", "Бугурусланский муниципальный район"),
    21: ("Бузулукский район", "Бузулукский муниципальный район"),
    22: ("Гайский МО", "Гайский"),
    23: ("Грачёвский район", "Грачёвский муниципальный район"),
    24: ("Домбаровский район", "Домбаровский муниципальный район"),
    25: ("Илекский район", "Илекский муниципальный район"),
    26: ("Кваркенский район", "Кваркенский муниципальный район"),
    27: ("Красногвардейский район", "Красногвардейский муниципальный район"),
    28: ("Кувандыкский МО", "Кувандыкский"),
    29: ("Курманаевский район", "Курманаевский муниципальный район"),
    30: ("Матвеевский район", "Матвеевский муниципальный район"),
    31: ("Новоорский район", "Новоорский муниципальный район"),
    32: ("Новосергиевский район", "Новосергиевский муниципальный район"),
    33: ("Октябрьский район", "Октябрьский муниципальный район"),
    34: ("Оренбургский район", "Оренбургский муниципальный район"),
    35: ("Первомайский район", "Первомайский муниципальный район"),
    36: ("Переволоцкий район", "Переволоцкий муниципальный район"),
    37: ("Пономарёвский район", "Пономарёвский муниципальный район"),
    38: ("Сакмарский район", "Сакмарский муниципальный район"),
    39: ("Саракташский район", "Саракташский муниципальный район"),
    40: ("Светлинский район", "Светлинский муниципальный район"),
    41: ("Северный район", "Северный муниципальный район"),
    42: ("Соль-Илецкий МО", "Соль-Илецкий"),
    43: ("Сорочинский МО", "Сорочинский"),
    44: ("Ташлинский район", "Ташлинский муниципальный район"),
    45: ("Тоцкий район", "Тоцкий муниципальный район"),
    46: ("Тюльганский район", "Тюльганский муниципальный район"),
    47: ("Шарлыкский район", "Шарлыкский муниципальный район"),
    48: ("Ясненский МО", "Ясненский"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("geojson", type=Path)
    parser.add_argument("--count", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20_260_810)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def polygons(geometry: dict[str, Any]) -> list[list[list[list[float]]]]:
    coordinates = geometry["coordinates"]
    if geometry["type"] == "Polygon":
        return [coordinates]
    if geometry["type"] == "MultiPolygon":
        return coordinates
    raise ValueError(f"Unsupported geometry: {geometry['type']}")


def point_in_ring(x: float, y: float, ring: list[list[float]]) -> bool:
    inside = False
    previous = ring[-1]
    for current in ring:
        x1, y1 = previous[:2]
        x2, y2 = current[:2]
        if (y1 > y) != (y2 > y):
            crossing_x = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < crossing_x:
                inside = not inside
        previous = current
    return inside


def point_in_polygon(x: float, y: float, polygon: list[list[list[float]]]) -> bool:
    return point_in_ring(x, y, polygon[0]) and not any(
        point_in_ring(x, y, hole) for hole in polygon[1:]
    )


def polygon_area(polygon: list[list[list[float]]]) -> float:
    ring = polygon[0]
    area = 0.0
    for previous, current in zip(ring, ring[1:]):
        area += previous[0] * current[1] - current[0] * previous[1]
    return abs(area) / 2


def random_point(
    candidates: list[list[list[list[float]]]], rng: random.Random
) -> tuple[float, float]:
    weights = [max(polygon_area(candidate), 1e-12) for candidate in candidates]
    polygon = rng.choices(candidates, weights=weights, k=1)[0]
    outer = polygon[0]
    min_x = min(point[0] for point in outer)
    max_x = max(point[0] for point in outer)
    min_y = min(point[1] for point in outer)
    max_y = max(point[1] for point in outer)

    for _ in range(20_000):
        x = rng.uniform(min_x, max_x)
        y = rng.uniform(min_y, max_y)
        if point_in_polygon(x, y, polygon):
            return y, x
    raise RuntimeError("Could not sample a point inside municipality polygon")


def main() -> None:
    args = parse_args()
    if args.count < 1:
        raise ValueError("count must be positive")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        sys.stdout = args.output.open("w", encoding="utf-8", newline="\n")
    else:
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")

    collection = json.loads(args.geojson.read_text(encoding="utf-8"))
    features = {feature["properties"]["name"]: feature for feature in collection["features"]}
    missing = sorted({feature_name for _, feature_name in MUNICIPALITIES.values()} - features.keys())
    if missing:
        raise ValueError(f"Missing municipality polygons: {', '.join(missing)}")

    rng = random.Random(args.seed)
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    print("\\set ON_ERROR_STOP on")
    print("BEGIN;")
    print("CREATE TEMP TABLE load_test_locations (")
    print("  external_card_number text PRIMARY KEY,")
    print("  municipality_id integer NOT NULL,")
    print("  address text NOT NULL,")
    print("  latitude double precision NOT NULL,")
    print("  longitude double precision NOT NULL")
    print(");")
    print("COPY load_test_locations FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t');")

    municipality_ids = sorted(MUNICIPALITIES)
    for number in range(1, args.count + 1):
        municipality_id = municipality_ids[(number - 1) % len(municipality_ids)]
        municipality_name, feature_name = MUNICIPALITIES[municipality_id]
        latitude, longitude = random_point(polygons(features[feature_name]["geometry"]), rng)
        address = (
            f"Оренбургская область, {municipality_name}, "
            f"место пожара №{number:05d}"
        )
        writer.writerow(
            (
                f"LOADTEST-20260810-{number:05d}",
                municipality_id,
                address,
                f"{latitude:.6f}",
                f"{longitude:.6f}",
            )
        )

    print("\\.")
    print("UPDATE fires AS fire")
    print("SET municipality_id = location.municipality_id,")
    print("    address = location.address,")
    print("    latitude = location.latitude,")
    print("    longitude = location.longitude")
    print("FROM load_test_locations AS location")
    print("WHERE fire.external_card_number = location.external_card_number;")
    print("SELECT count(*) AS updated_load_test_fires")
    print("FROM fires AS fire")
    print("JOIN load_test_locations AS location")
    print("  ON location.external_card_number = fire.external_card_number")
    print("WHERE fire.address = location.address")
    print("  AND fire.latitude = location.latitude")
    print("  AND fire.longitude = location.longitude;")
    print("COMMIT;")


if __name__ == "__main__":
    main()
