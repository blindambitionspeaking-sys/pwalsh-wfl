from rest_framework import serializers

from wind_for_life.apps.anemometers.models import Anemometer
from wind_for_life.apps.anemometers.serializers import ReadingMinimalSerializer


# Endpoint Specific
class RecentReadingsAnemometerSerializer(serializers.ModelSerializer):
    average_daily_speed = serializers.FloatField()
    average_weekly_speed = serializers.FloatField()
    recent_readings = serializers.SerializerMethodField()

    class Meta:  # type: ignore  # noqa: PGH003
        model = Anemometer
        fields = [
            "id",
            "name",
            "longitude",
            "latitude",
            "average_daily_speed",
            "average_weekly_speed",
            "recent_readings",
        ]
        read_only_fields = ["id"]

    def get_recent_readings(self, anemometer):
        recent = anemometer.readings.order_by("-recorded_at")[:5]
        return ReadingMinimalSerializer(recent, many=True).data
