"Unit tests for appointments"
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from unittest.mock import patch

from botocore.exceptions import BotoCoreError
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from . import views
from .models import Appointment, Hairdresser, Service

SERVICE_HAIRCUT = 1
HAIRDRESSER_1 = 1
FAKE_NOW = datetime(2010, 1, 1, 8, 0, tzinfo=ZoneInfo("America/Los_Angeles"))


class AnnouncementTests(TestCase):
    "Tests for loading announcement messages from DynamoDB."

    @patch("appointments.views.boto3.client")
    def test_get_announcements_reads_dynamodb_items(self, mock_boto_client):
        "Test announcements are read from DynamoDB."
        mock_dynamodb = mock_boto_client.return_value
        mock_dynamodb.scan.return_value = {
            "Items": [
                {"Contents": {"S": "We are open late today."}},
                {"Contents": {"S": "Walk-ins welcome."}},
                {"Contents": {"S": ""}},
                {},
            ]
        }

        announcements = views.get_announcements()

        self.assertEqual(
            announcements,
            ["We are open late today.", "Walk-ins welcome."],
        )
        mock_dynamodb.scan.assert_called_once_with(TableName="DEV_Announcement")

    @patch("appointments.views.boto3.client")
    def test_get_announcements_returns_empty_list_when_dynamodb_fails(
        self, mock_boto_client
    ):
        "Test DynamoDB errors do not break the page."
        mock_boto_client.side_effect = BotoCoreError()

        announcements = views.get_announcements()

        self.assertEqual(announcements, [])


class AppointmentViewTests(TestCase):
    "Tests for appointment views and scheduling helpers"

    def setUp(self):
        "Create a request factory for direct view calls."
        self.factory = RequestFactory()
        self.announcements_patch = patch(
            "appointments.views.get_announcements", return_value=[]
        )
        self.announcements_patch.start()
        self.addCleanup(self.announcements_patch.stop)

    def get_index_context(self, service_id=None, hairdresser_id=None, date_string=None):
        "Return the context passed to the index template."
        request = self.factory.get("/")

        with patch("appointments.views.render") as mock_render:
            mock_render.return_value = HttpResponse()
            views.index(request, service_id, hairdresser_id, date_string)

        return mock_render.call_args[0][2]

    def test_intervals_overlap(self):
        "Test overlapping, adjacent, and separate time windows."
        start = FAKE_NOW.replace(hour=9)
        end = start + timedelta(hours=1)

        self.assertTrue(
            views.intervals_overlap(
                start, end, start + timedelta(minutes=30), end + timedelta(minutes=30)
            )
        )
        self.assertFalse(
            views.intervals_overlap(start, end, end, end + timedelta(hours=1))
        )
        self.assertFalse(
            views.intervals_overlap(
                start, end, end + timedelta(minutes=30), end + timedelta(hours=1)
            )
        )

    @patch("django.utils.timezone.now")
    def test_build_start_times_marks_past_and_overlapping_slots(self, mock_now):
        "Test that unavailable start times are blocked."
        mock_now.return_value = FAKE_NOW.replace(hour=9, minute=15)
        day_start = FAKE_NOW.replace(hour=9, minute=0)
        blocked_start = FAKE_NOW.replace(hour=10, minute=0)
        blocked_times = [(blocked_start, blocked_start + timedelta(hours=1))]

        start_times = views.build_start_times(day_start, 60, blocked_times)
        slots = {slot["time_formatted"]: slot for slot in start_times}

        self.assertEqual(len(start_times), 18)
        self.assertTrue(slots["09:00"]["is_blocked"])
        self.assertTrue(slots["10:00"]["is_blocked"])
        self.assertTrue(slots["10:30"]["is_blocked"])
        self.assertFalse(slots["11:00"]["is_blocked"])

    def test_index_lists_services(self):
        "Test the first index step lists services."
        context = self.get_index_context()

        self.assertEqual(context["services_all"].count(), 3)
        self.assertNotIn("hairdressers_all", context)

    def test_index_service_step_lists_hairdressers(self):
        "Test selecting a service adds hairdressers to the context."
        context = self.get_index_context(service_id=SERVICE_HAIRCUT)

        self.assertEqual(context["selected_service_id"], SERVICE_HAIRCUT)
        self.assertEqual(context["hairdressers_all"].count(), 2)
        self.assertNotIn("dates_all", context)

    @patch("django.utils.timezone.now")
    def test_index_hairdresser_step_lists_dates(self, mock_now):
        "Test selecting a hairdresser adds upcoming dates."
        mock_now.return_value = FAKE_NOW

        context = self.get_index_context(
            service_id=SERVICE_HAIRCUT, hairdresser_id=HAIRDRESSER_1
        )

        self.assertEqual(context["selected_hairdresser_id"], HAIRDRESSER_1)
        self.assertEqual(len(context["dates_all"]), 7)
        self.assertEqual(context["dates_all"][0][1], "20100101")
        self.assertNotIn("start_times_all", context)

    @patch("django.utils.timezone.now")
    def test_index_date_step_blocks_booked_time(self, mock_now):
        "Test selected date start times exclude existing appointments."
        mock_now.return_value = FAKE_NOW
        service = Service.objects.get(pk=SERVICE_HAIRCUT)
        hairdresser = Hairdresser.objects.get(pk=HAIRDRESSER_1)
        start_datetime = timezone.make_aware(datetime(2010, 1, 1, 12, 0))

        Appointment.objects.create(
            service=service,
            hairdresser=hairdresser,
            start_datetime=start_datetime,
            end_datetime=start_datetime + timedelta(minutes=service.duration),
            customer_contact="+49123456789",
        )

        context = self.get_index_context(
            service_id=SERVICE_HAIRCUT,
            hairdresser_id=HAIRDRESSER_1,
            date_string="20100101",
        )
        slots = {
            slot["time_formatted"]: slot
            for slot in context["start_times_all"]
        }

        self.assertEqual(context["selected_date"], "20100101")
        self.assertEqual(context["start_times_available_count"], 15)
        self.assertTrue(slots["12:00"]["is_blocked"])
        self.assertFalse(slots["13:00"]["is_blocked"])

    def test_create_get_redirects_without_creating_appointment(self):
        "Test GET requests redirect without creating appointments."
        response = self.client.get(reverse("create"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("index"))
        self.assertEqual(Appointment.objects.count(), 0)

    @patch("django.utils.timezone.now")
    def test_create_post_reduces_available_start_times(self, mock_now):
        "Test creating an appointment reduces the available start time count."
        mock_now.return_value = FAKE_NOW
        context = self.get_index_context(
            service_id=SERVICE_HAIRCUT,
            hairdresser_id=HAIRDRESSER_1,
            date_string="20100101",
        )
        available_before = context["start_times_available_count"]

        self.client.post(
            reverse("create"),
            {
                "service": SERVICE_HAIRCUT,
                "hairdresser": HAIRDRESSER_1,
                "date": "20100101",
                "appointment_time": "12:00",
                "customer_contact": "+49123456789",
            },
        )

        context = self.get_index_context(
            service_id=SERVICE_HAIRCUT,
            hairdresser_id=HAIRDRESSER_1,
            date_string="20100101",
        )
        available_after = context["start_times_available_count"]

        self.assertLess(available_after, available_before)

    def test_create_post_creates_appointment(self):
        "Test POST requests create an appointment."
        response = self.client.post(
            reverse("create"),
            {
                "service": SERVICE_HAIRCUT,
                "hairdresser": HAIRDRESSER_1,
                "date": "20100101",
                "appointment_time": "12:00",
                "customer_contact": "+49123456789",
            },
        )
        appointment = Appointment.objects.get()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("index"))
        self.assertEqual(appointment.service_id, SERVICE_HAIRCUT)
        self.assertEqual(appointment.hairdresser_id, HAIRDRESSER_1)
        self.assertEqual(timezone.localtime(appointment.start_datetime).hour, 12)
        self.assertEqual(appointment.customer_contact, "+49123456789")
