"""API views for science literature search."""

from __future__ import annotations

import logging
from typing import Any

from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .services.pipeline import run_search_pipeline

logger = logging.getLogger(__name__)


class ScienceSearchView(APIView):
    """
    POST /api/search/

    Accepts ``{ "query": "..." }`` and returns credible bibliographic sources.
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes: list = []

    def post(self, request: Request) -> Response:
        """Run the science search middleware pipeline."""
        query = request.data.get("query")
        if not isinstance(query, str) or not query.strip():
            return Response(
                {"success": False, "error": "Field 'query' must be a non-empty string."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(query) > 500:
            return Response(
                {"success": False, "error": "Query must be 500 characters or fewer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payload: dict[str, Any] = run_search_pipeline(query.strip())
            http_status = status.HTTP_200_OK if payload.get("success") else status.HTTP_400_BAD_REQUEST
            return Response(payload, status=http_status)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Science search failed")
            return Response(
                {
                    "success": False,
                    "error": "Search pipeline failed.",
                    "detail": str(exc),
                    "results": [],
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get(self, request: Request) -> Response:
        """Allow simple GET ?q= for browser smoke tests."""
        query = request.query_params.get("q") or request.query_params.get("query")
        if not query:
            return Response(
                {
                    "success": True,
                    "message": 'POST JSON {"query": "your science question"} to this endpoint.',
                }
            )
        try:
            payload = run_search_pipeline(query.strip())
            return Response(payload)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Science search failed")
            return Response(
                {
                    "success": False,
                    "error": "Search pipeline failed.",
                    "detail": str(exc),
                    "results": [],
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
