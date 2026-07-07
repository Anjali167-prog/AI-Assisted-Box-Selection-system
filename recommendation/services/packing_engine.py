from dataclasses import dataclass
from itertools import permutations

from boxes.models import Box
from products.models import Product


@dataclass
class Void:
    x: float
    y: float
    z: float
    length: float
    width: float
    height: float

    @property
    def volume(self) -> float:
        return self.length * self.width * self.height


@dataclass
class Placement:
    product_id: int
    x: float
    y: float
    z: float
    length: float
    width: float
    height: float


def _unique_orientations(length: float, width: float, height: float) -> list[tuple[float, float, float]]:
    seen: set[tuple[float, float, float]] = set()
    result: list[tuple[float, float, float]] = []
    for p in permutations((length, width, height)):
        if p not in seen:
            seen.add(p)
            result.append(p)
    return result


def _fits_in_void(item_dims: tuple[float, float, float], void: Void) -> bool:
    il, iw, ih = item_dims
    return il <= void.length and iw <= void.width and ih <= void.height


def _overlaps(
    placements: list[Placement],
    x: float, y: float, z: float,
    length: float, width: float, height: float,
) -> bool:
    for p in placements:
        if (p.x < x + length and p.x + p.length > x
                and p.y < y + width and p.y + p.width > y
                and p.z < z + height and p.z + p.height > z):
            return True
    return False


def _split_void(void: Void, item: tuple[float, float, float]) -> list[Void]:
    il, iw, ih = item
    new_voids: list[Void] = []

    right_l = void.length - il
    if right_l > 0:
        new_voids.append(
            Void(void.x + il, void.y, void.z, right_l, void.width, void.height)
        )

    front_w = void.width - iw
    if front_w > 0:
        new_voids.append(
            Void(void.x, void.y + iw, void.z, void.length, front_w, void.height)
        )

    top_h = void.height - ih
    if top_h > 0:
        new_voids.append(
            Void(void.x, void.y, void.z + ih, void.length, void.width, top_h)
        )

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

    voids: list[Void] = [
        Void(0, 0, 0, float(box.length), float(box.width), float(box.height))
    ]
    placements: list[Placement] = []
    orientation_cache: dict[int, list[tuple[float, float, float]]] = {}

    for product in expanded:
        if product.id not in orientation_cache:
            orientation_cache[product.id] = _unique_orientations(
                float(product.length), float(product.width), float(product.height)
            )
        orientations = orientation_cache[product.id]

        placed = False
        for void in sorted(voids, key=lambda v: v.volume, reverse=True):
            for orient in orientations:
                if _fits_in_void(orient, void):
                    il, iw, ih = orient
                    if _overlaps(
                        placements,
                        void.x, void.y, void.z,
                        il, iw, ih,
                    ):
                        continue
                    placements.append(
                        Placement(
                            product_id=product.id,
                            x=void.x,
                            y=void.y,
                            z=void.z,
                            length=il,
                            width=iw,
                            height=ih,
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
