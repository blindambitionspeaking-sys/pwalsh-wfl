from django.core.management.base import BaseCommand

from wind_for_life.apps.anemometers.tests.factories import AnemometerFactory


class Command(BaseCommand):
    help = "Displays current time"

    def add_arguments(self, parser):
        parser.add_argument(
            "num_anemometers",
            type=int,
            help="Indicates the number of anemometers to be created",
        )
        parser.add_argument(
            "num_readings",
            default=0,
            type=int,
            help="Indicates the number of readings per anemometer to be created",
        )
        parser.add_argument(
            "num_tags",
            default=0,
            type=int,
            help="Indicates the number of tags per readings to be created",
        )

    def handle(self, *args, **kwargs):
        num_anemometers = kwargs["num_anemometers"]
        num_readings = kwargs["num_readings"]
        num_tags = kwargs["num_tags"]

        AnemometerFactory.create_batch(
            num_anemometers,
            readings=num_readings,
            readings__num_tags=num_tags,
        )
