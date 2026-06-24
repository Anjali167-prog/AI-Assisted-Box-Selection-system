from dataclasses import dataclass
from itertools import permutations
from typing import Iterator

from boxes.models import Box
from orders.models import Order
from products.models import Product


@dataclass
class Void:
    x: float
    y: float
    z: float
    l: float
    w: float
    h: float

    @property
    def volume(self) -> float:
        return self.l * self.w * self.h


@dataclass
class Placement:
    product_id: int
    x: float
    y: float
    z: float
    l: float
    w: float
    h: float


def _unique_orientations(l: float, w: float, h: float) -> list[tuple[float, float, float]]:
    seen: set[tuple[float, float, float]] = set()
    result: list[tuple[float, float, float]] = []
    for p in permutations((l, w, h)):
        if p not in seen:
            seen.add(p)
            result.append(p)
    return result


def _fits_in_void(item_dims: tuple[float, float, float], void: Void) -> bool:
    il, iw, ih = item_dims
    return il <= void.l and iw <= void.w and ih <= void.h


def _split_void(void: Void, item: tuple[float, float, float]) -> list[Void]:
    il, iw, ih = item
    new_voids: list[Void] = []

    right_l = void.l - il
    if right_l > 0:
        new_voids.append(Void(void.x + il, void.y, void.z, right_l, void.w, void.h))

    front_w = void.w - iw
    if front_w > 0:
        new_voids.append(Void(void.x, void.y + iw, void.z, void.l, front_w, void.h))

    top_h = void.h - ih
    if top_h > 0:
        new_voids.append(Void(void.x, void.y, void.z + ih, void.l, void.w, top_h))

    return new_voids


def can_fit(
    products: list[tuple[Product, int]],
    box: Box,
) -> tuple[bool, list[Placement] | None]:
    total_weight = sum(p.weight * qty for p, qty in products)
    if total_weight > box.max_weight:
        return False, None

    expanded: list[Product] = []
    for product, qty in products:
        expanded.extend([product] * qty)
    expanded.sort(
        key=lambda p: p.length * p.width * p.height,
        reverse=True,
    )

    voids: list[Void] = [Void(0, 0, 0, box.length, box.width, box.height)]
    placements: list[Placement] = []
    orientation_cache: dict[int, list[tuple[float, float, float]]] = {}

    for product in expanded:
        if product.id not in orientation_cache:
            orientation_cache[product.id] = _unique_orientations(
                product.length, product.width, product.height
            )
        orientations = orientation_cache[product.id]

        placed = False
        for void in sorted(voids, key=lambda v: v.volume, reverse=True):
            for orient in orientations:
                if _fits_in_void(orient, void):
                    il, iw, ih = orient
                    placements.append(
                        Placement(
                            product_id=product.id,
                            x=void.x,
                            y=void.y,
                            z=void.z,
                            l=il,
                            w=iw,
                            h=ih,
                        )
                    )
                    new_voids = _split_void(void, orient)
                    voids.remove(void)
                    voids.extend(new_voids)
                    placed = True
                    break
            if placed:
                break
        if not placed:
            return False, None

    return True, placements
