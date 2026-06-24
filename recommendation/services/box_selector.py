from django.conf import settings
from django.db.models import ExpressionWrapper, F, FloatField
from django.shortcuts import get_object_or_404

from boxes.models import Box
from orders.models import Order
from products.models import Product

from .ai_explainer import AIRecommendationExplainer
from .packing_engine import can_fit


def recommend_box(order_id: int) -> dict | None:
    order = get_object_or_404(Order, pk=order_id)
    items = list(order.items.select_related("product"))

    if not items:
        return None

    product_qty: list[tuple[Product, int]] = [
        (item.product, item.quantity) for item in items
    ]

    total_volume = sum(
        item.product.length * item.product.width * item.product.height * item.quantity
        for item in items
    )
    total_weight = sum(item.product.weight * item.quantity for item in items)

    boxes = Box.objects.filter(
        max_weight__gte=total_weight,
    ).annotate(
        box_volume=ExpressionWrapper(
            F("length") * F("width") * F("height"),
            output_field=FloatField(),
        ),
    ).order_by("cost", "box_volume")

    for box in boxes:
        if box.box_volume < total_volume:
            continue

        box_dims = sorted([box.length, box.width, box.height])
        all_fit_dimensionally = True
        for product, _ in product_qty:
            product_dims = sorted([product.length, product.width, product.height])
            if any(pd > bd for pd, bd in zip(product_dims, box_dims)):
                all_fit_dimensionally = False
                break
        if not all_fit_dimensionally:
            continue

        fits, placements = can_fit(product_qty, box)
        if fits:
            api_key = getattr(settings, "GROK_API_KEY", None)
            explanation = None
            if api_key:
                explainer = AIRecommendationExplainer(api_key=api_key)
                explanation = explainer.explain(
                    box_name=box.name,
                    cost=str(box.cost),
                    total_items=sum(qty for _, qty in product_qty),
                    total_weight=float(total_weight),
                    total_volume=float(total_volume),
                    box_volume=float(box.box_volume),
                    box_max_weight=float(box.max_weight),
                )

            return {
                "box_id": box.id,
                "box_name": box.name,
                "cost": str(box.cost),
                "box_dimensions": {
                    "length": box.length,
                    "width": box.width,
                    "height": box.height,
                },
                "box_max_weight": box.max_weight,
                "volume_utilization_pct": round(
                    (float(total_volume) / box.box_volume) * 100, 1
                ),
                "placements": [
                    {
                        "product_id": p.product_id,
                        "position": {"x": p.x, "y": p.y, "z": p.z},
                        "orientation": {"length": p.l, "width": p.w, "height": p.h},
                    }
                    for p in placements
                ],
                "explanation": explanation,
            }

    return None
