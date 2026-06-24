from django.http import Http404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from .services.box_selector import recommend_box


@api_view(["POST"])
def recommend_box_view(request: Request) -> Response:
    order_id = request.data.get("order_id")

    if order_id is None:
        return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        result = recommend_box(order_id)
    except Http404:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    if result is None:
        return Response(
            {"order_id": order_id, "recommendation": None},
            status=status.HTTP_200_OK,
        )

    return Response(
        {"order_id": order_id, "recommendation": result},
        status=status.HTTP_200_OK,
    )
