import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from wind_for_life.apps.anemometers.filters import ReadingFilterSet
from wind_for_life.apps.anemometers.models import Reading
from wind_for_life.apps.anemometers.tests.factories import (
    AnemometerFactory,
    ReadingFactory,
)
from wind_for_life.apps.users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="testpass")  # noqa: S106


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user)
    return api_client


# ----------------------------
# 🔍 ANEMOMETER VIEWSET TESTS
# ----------------------------


def test_anemometer_detail(auth_client):
    anemometer_with_readings = AnemometerFactory(readings=5)
    url = reverse(
        "api:anemometers-detail",
        kwargs={"pk": anemometer_with_readings.pk},
    )
    response = auth_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == str(anemometer_with_readings.pk)


def test_recent_readings_view(auth_client):
    num_anemometers = 5
    multiple_anemometers = AnemometerFactory.create_batch(num_anemometers)
    url = reverse("api:anemometers-recent-readings")
    response = auth_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == len(multiple_anemometers)
    first_result = response.data["results"][0]
    assert "recent_readings" in first_result
    assert "average_daily_speed" in first_result
    assert "average_weekly_speed" in first_result


def test_anemometer_detail_not_found(auth_client):
    url = reverse(
        "api:anemometers-detail",
        kwargs={"pk": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"},
    )
    response = auth_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


# ------------------------
# 📈 READING VIEWSET TESTS
# ------------------------


def test_reading_list(auth_client):
    number_of_readings = 5
    ReadingFactory.create_batch(number_of_readings)
    url = reverse("api:readings-list")
    response = auth_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) >= number_of_readings


def test_create_reading(auth_client):
    anemometer = AnemometerFactory()
    url = reverse("api:readings-list")
    payload = {
        "speed": 14.2,
        "recorded_at": "2025-06-21T10:00:00Z",
        "anemometer": str(anemometer.pk),
        "tags": ["gusty", "chilly"],
    }
    response = auth_client.post(url, data=payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert Reading.objects.filter(anemometer=anemometer.pk).exists()


def test_patch_reading(auth_client):
    reading = ReadingFactory(speed=5.0)
    new_speed = 8.9
    url = reverse("api:readings-detail", kwargs={"pk": reading.pk})
    response = auth_client.patch(url, {"speed": new_speed}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["speed"] == new_speed


# -------------------------------------
# 📌 NESTED ANEMOMETER READING VIEWSET
# -------------------------------------


def test_nested_reading_list(auth_client):
    number_of_readings = 5
    anemometer_with_readings = AnemometerFactory(readings=number_of_readings)
    url = reverse(
        "api:anemometers-readings-list",
        kwargs={"anemometer_pk": anemometer_with_readings.pk},
    )
    response = auth_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == number_of_readings


def test_nested_reading_detail(auth_client):
    anemometer_with_readings = AnemometerFactory(readings=5)
    reading = anemometer_with_readings.readings.first()
    url = reverse(
        "api:anemometers-readings-detail",
        kwargs={
            "anemometer_pk": anemometer_with_readings.pk,
            "pk": reading.pk,
        },
    )
    response = auth_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == str(reading.pk)


def test_nested_reading_not_found(auth_client):
    anemometer_with_readings = AnemometerFactory(readings=5)
    url = reverse(
        "api:anemometers-readings-detail",
        kwargs={
            "anemometer_pk": anemometer_with_readings.pk,
            "pk": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        },
    )
    response = auth_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


# PERMISSIONS


@pytest.mark.django_db(transaction=True)
def test_unauthenticated_user_cannot_access_anemometers(api_client):
    url = reverse("api:anemometers-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db(transaction=True)
def test_unauthenticated_user_cannot_create_reading(api_client):
    anemometer = AnemometerFactory()
    url = reverse("api:readings-list")
    payload = {
        "speed": 12.0,
        "recorded_at": "2025-06-21T10:00:00Z",
        "anemometer": str(anemometer.pk),
        "tags": ["gusty"],
    }
    response = api_client.post(url, payload, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


# INVALID INPUT


def test_create_reading_with_missing_fields(auth_client):
    url = reverse("api:readings-list")
    payload = {"speed": 10.5}  # missing anemometer and recorded_at
    response = auth_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "anemometer" in response.data


def test_create_reading_with_invalid_speed(auth_client):
    anemometer = AnemometerFactory()
    url = reverse("api:readings-list")
    payload = {
        "speed": "invalid",  # not a float
        "recorded_at": "2025-06-21T10:00:00Z",
        "anemometer": str(anemometer.pk),
    }
    response = auth_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "speed" in response.data


# POST, PUT, PATCH validations


def test_update_anemometer_name(auth_client):
    anemometer = AnemometerFactory(name="Old Name")
    url = reverse("api:anemometers-detail", kwargs={"pk": anemometer.pk})
    response = auth_client.patch(url, {"name": "Updated Name"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Updated Name"


def test_create_reading_with_tags(auth_client):
    anemometer = AnemometerFactory()
    url = reverse("api:readings-list")
    payload = {
        "speed": 9.8,
        "recorded_at": "2025-06-21T08:00:00Z",
        "anemometer": str(anemometer.pk),
        "tags": ["gusty", "steady"],
    }
    response = auth_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert set(response.data["tags"]) == {"gusty", "steady"}


# INVALID ID


def test_reading_creation_fails_for_invalid_anemometer(auth_client):
    url = reverse("api:readings-list")
    payload = {
        "speed": 15.0,
        "recorded_at": "2025-06-21T12:00:00Z",
        "anemometer": "invalid-uuid",
    }
    response = auth_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "anemometer" in response.data


# TAGS


@pytest.fixture
def anemometer():
    return AnemometerFactory.create()


@pytest.fixture
def readings(anemometer):
    reading_gusty = ReadingFactory.create(anemometer=anemometer, tags=["gusty"])
    reading_gusty_drafty = ReadingFactory.create(
        anemometer=anemometer,
        tags=["gusty", "drafty"],
    )
    reading_drafty_stormy = ReadingFactory.create(
        anemometer=anemometer,
        tags=["drafty", "stormy"],
    )
    reading_calm = ReadingFactory.create(anemometer=anemometer, tags=["calm"])
    return {
        "gusty": reading_gusty,
        "gusty_drafty": reading_gusty_drafty,
        "drafty_stormy": reading_drafty_stormy,
        "calm": reading_calm,
    }


@pytest.mark.django_db
def test_filter_tags_any(readings):
    qs = Reading.objects.all()
    filterset = ReadingFilterSet(data={"tags_any": "gusty,drafty"}, queryset=qs)
    filtered_qs = filterset.qs

    assert readings["gusty"] in filtered_qs
    assert readings["gusty_drafty"] in filtered_qs
    assert readings["drafty_stormy"] in filtered_qs
    assert readings["calm"] not in filtered_qs


@pytest.mark.django_db
def test_filter_tags_exact_single_tag(readings):
    qs = Reading.objects.all()
    filterset = ReadingFilterSet(data={"tags_exact": "gusty"}, queryset=qs)
    filtered_qs = filterset.qs

    assert readings["gusty"] in filtered_qs
    assert readings["gusty_drafty"] not in filtered_qs
    assert readings["drafty_stormy"] not in filtered_qs
    assert readings["calm"] not in filtered_qs


@pytest.mark.django_db
def test_filter_tags_exact_multiple_tags(readings):
    qs = Reading.objects.all()
    filterset = ReadingFilterSet(
        data={"tags_exact": "gusty,drafty"},
        queryset=qs,
    )
    filtered_qs = filterset.qs

    assert readings["gusty_drafty"] in filtered_qs
    assert readings["gusty"] not in filtered_qs
    assert readings["drafty_stormy"] not in filtered_qs
    assert readings["calm"] not in filtered_qs
