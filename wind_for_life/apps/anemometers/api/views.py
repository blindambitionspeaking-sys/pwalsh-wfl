from datetime import timedelta
from io import StringIO
import csv
from pydoc import pager
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db.models import Avg
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.utils.timezone import now
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from wind_for_life.apps.anemometers.api.serializers import (
    RecentReadingsAnemometerSerializer,
)
from wind_for_life.apps.anemometers.filters import ReadingFilterSet
from wind_for_life.apps.anemometers.models import Anemometer, Reading
from wind_for_life.apps.anemometers.serializers import (
    AnemometerDetailSerializer,
    AnemometerMinimalSerializer,
    ReadingDetailSerializer,
    ReadingMinimalSerializer,
    ReadReadingMinimalSerializer,
    WriteReadingMinimalSerializer,
)
from wind_for_life.apps.base.mixins import ReadWriteSerializerMixin


class AnemometerViewSet(viewsets.ModelViewSet):
    """Anemometers API"""

    serializer_class = AnemometerMinimalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        return Anemometer.objects.all()

    def retrieve(self, request, pk=None):
        """Detail anemometer shows readings values as well"""
        try:
            anemometer = Anemometer.objects.prefetch_related("readings").get(
                pk=pk,
            )
        except Anemometer.DoesNotExist as exc:
            raise NotFound from exc

        serializer = AnemometerDetailSerializer(anemometer)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
    )
    def recent_readings(self, request):
        """
        Anemometers with average daily & weekly speed as well as their 5 most
        recent readings.
        """
        _now = now()
        day_ago = _now - timedelta(days=1)
        week_ago = _now - timedelta(days=7)

        anemometers = Anemometer.objects.prefetch_related("readings").annotate(
            average_daily_speed=Avg(
                "readings__speed",
                filter=Q(readings__recorded_at__gte=day_ago),
            ),
            average_weekly_speed=Avg(
                "readings__speed",
                filter=Q(readings__recorded_at__gte=week_ago),
            ),
        )

        page = self.paginate_queryset(anemometers)
        if page is not None:
            serializer = RecentReadingsAnemometerSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = RecentReadingsAnemometerSerializer(anemometers, many=True)
        return Response(serializer.data)
    

class ReadingViewSet(ReadWriteSerializerMixin, viewsets.ModelViewSet):
    """Readings API"""

    queryset = Reading.objects.all()
    read_serializer_class = ReadReadingMinimalSerializer
    write_serializer_class = WriteReadingMinimalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ReadingFilterSet

    def retrieve(self, request, pk=None):
        """Detailed reading shows anemometer value as well"""
        try:
            reading = Reading.objects.select_related("anemometer").get(
                pk=pk,
            )
        except Reading.DoesNotExist as exc:
            raise NotFound from exc

        serializer = ReadingDetailSerializer(reading)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"], url_path="export")
    def export(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        export_format = request.query_params.get("format", "json").lower()
       
        # Handle pagination if requested
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
            paginated_response = self.get_paginated_response(data)
       
        if export_format == "csv":
            return self._export_csv(paginated_response.data["results"])
        elif export_format == "json":
            return paginated_response
        else:
            return paginated_response  # Default to JSON


class AnemometerReadingViewSet(viewsets.ModelViewSet):
    """Readings nested into anemometers

    Allows to get anemometer specific readings operations.
    Optimized for getting anemometer data coupled with reading's.
    """

    serializer_class = ReadingMinimalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        return Reading.objects.select_related("anemometer").filter(
            anemometer=self.kwargs["anemometer_pk"],
        )

from io import StringIO
import csv
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.response import Response

class ReadingViewSet(ReadWriteSerializerMixin, viewsets.ModelViewSet):
    # existing class body...

    @action(detail=False, methods=["GET"], url_path="export")
    def export(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        export_format = request.query_params.get("format", "json").lower()

        if export_format == "csv":
            return self._export_csv(serializer.data)

        return Response(serializer.data)

    def _export_csv(self, data):
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["id", "speed", "recorded_at", "tags"])

        for item in data:
            tags = ",".join(item.get("tags", []))
            writer.writerow([item["id"], item["speed"], item["recorded_at"], tags])

        response = HttpResponse(buffer.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="readings.csv"'
        return response


    def retrieve(self, request, anemometer_pk, pk=None):
        """Detailed reading shows anemometer value as well"""
        try:
            reading = Reading.objects.select_related("anemometer").get(
                pk=pk,
            )
        except Reading.DoesNotExist as exc:
            raise NotFound from exc

        serializer = ReadingDetailSerializer(reading)
        return Response(serializer.data)
