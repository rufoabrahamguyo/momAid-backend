"""Seed reference data for development and demos."""

from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.exercises.models import Exercise
from apps.healthcare.models import Hospital
from apps.partner.models import PartnerTask
from apps.remedies.models import BabyCondition, Remedy


class Command(BaseCommand):
    help = "Seed baby conditions/remedies, exercises, partner tasks, and hospitals."

    def handle(self, *args, **options) -> None:
        self._seed_remedies()
        self._seed_exercises()
        self._seed_partner_tasks()
        self._seed_hospitals()
        self.stdout.write(self.style.SUCCESS("Seed complete."))

    def _seed_remedies(self) -> None:
        data = [
            (
                "Colic",
                "😣",
                [
                    ("Bicycle legs", "Gently move baby's legs in a cycling motion.", 5, ""),
                    ("Warm bath", "A warm soak can relax tummy muscles.", 15, ""),
                    ("Tummy time", "Short supervised tummy time when awake.", 10, ""),
                ],
            ),
            (
                "Teething",
                "🦷",
                [
                    ("Chilled teether", "Offer a chilled (not frozen) teething ring.", None, ""),
                    ("Gum massage", "Clean finger, gentle circular gum massage.", 5, ""),
                    ("Cold washcloth", "Damp washcloth chilled in fridge.", None, ""),
                ],
            ),
            (
                "Congestion",
                "🤧",
                [
                    ("Saline drops", "Use saline and suction per pediatric guidance.", None, ""),
                    ("Humidifier", "Cool-mist humidifier in the nursery.", None, ""),
                    ("Elevate head", "Slightly elevate crib mattress per safe-sleep guidance.", None, ""),
                ],
            ),
            (
                "Diaper rash",
                "🧴",
                [
                    ("Air time", "Let skin breathe without diaper for short periods.", 10, ""),
                    ("Barrier cream", "Zinc oxide barrier with each change.", None, ""),
                    ("Frequent changes", "Change promptly; pat dry gently.", None, ""),
                ],
            ),
            (
                "Reflux",
                "🍼",
                [
                    ("Upright feeding", "Keep baby upright during feeds.", None, ""),
                    ("Burping", "Pause to burp mid-feed.", 5, ""),
                    ("Smaller feeds", "Offer smaller volumes more often if advised.", None, ""),
                ],
            ),
            (
                "Sleep challenges",
                "😴",
                [
                    ("Consistent routine", "Same order of calming steps nightly.", None, ""),
                    ("Dim lights", "Lower lights 30 minutes before sleep.", None, ""),
                    ("Sound machine", "Low white noise if pediatrician approves.", None, ""),
                ],
            ),
        ]
        for idx, (name, icon, remedies) in enumerate(data):
            c, _ = BabyCondition.objects.update_or_create(
                name=name,
                defaults={"icon": icon, "order": idx},
            )
            for i, (title, desc, dur, gif) in enumerate(remedies):
                Remedy.objects.update_or_create(
                    condition=c,
                    title=title,
                    defaults={
                        "description": desc,
                        "duration_minutes": dur,
                        "gif_url": gif or "",
                        "order": i,
                    },
                )

    def _seed_exercises(self) -> None:
        exercises = [
            (
                "Pelvic tilts",
                "Gentle pelvic tilts lying on your back with knees bent.",
                "https://example.com/videos/pelvic-tilts",
                "",
                120,
            ),
            (
                "Deep breathing",
                "Diaphragmatic breathing to calm the nervous system.",
                "https://example.com/videos/breathing",
                "",
                120,
            ),
            (
                "Neck & shoulder rolls",
                "Slow rolls to release upper back tension.",
                "https://example.com/videos/rolls",
                "",
                120,
            ),
            (
                "Glute bridge",
                "Bridge with feet hip-width; squeeze glutes at top.",
                "https://example.com/videos/bridge",
                "",
                120,
            ),
            (
                "Side-lying clamshell",
                "Open knees like a clamshell for hip stability.",
                "https://example.com/videos/clamshell",
                "",
                120,
            ),
        ]
        for i, (title, desc, video, thumb, dur) in enumerate(exercises):
            Exercise.objects.update_or_create(
                title=title,
                defaults={
                    "description": desc,
                    "video_url": video,
                    "thumbnail_url": thumb,
                    "duration_seconds": dur,
                    "order": i,
                },
            )

    def _seed_partner_tasks(self) -> None:
        blocks = [
            (0, 4, "Night feed support", "Take the night bottle / burping shift so mother can sleep.", 0),
            (0, 4, "Diaper station", "Stock diapers, wipes, and creams at each changing spot.", 1),
            (4, 12, "Tummy time cheer", "Lead 5 minutes of supervised tummy time.", 0),
            (4, 12, "Laundry loop", "Run a daily load of baby clothes and burp cloths.", 1),
            (12, 24, "Meal prep", "Prep one-handed snacks for the nursing parent.", 0),
            (12, 24, "Walk together", "Stroller walk for fresh air (15+ minutes).", 1),
            (24, 520, "Date check-in", "Schedule a 20-minute check-in about how baby is doing.", 0),
            (24, 520, "Pediatrician logistics", "Add next well-bvisit to shared calendar.", 1),
        ]
        for mn, mx, title, desc, ord_ in blocks:
            PartnerTask.objects.update_or_create(
                title=title,
                baby_age_weeks_min=mn,
                baby_age_weeks_max=mx,
                defaults={"description": desc, "order": ord_},
            )

    def _seed_hospitals(self) -> None:
        hospitals = [
            (
                "City General Hospital",
                "100 Main St, Metro City",
                40.7128000,
                -74.0060000,
                "+15555550100",
                True,
                True,
                True,
            ),
            (
                "Riverside Women's & Children's",
                "22 River Rd, Metro City",
                40.7200000,
                -74.0100000,
                "+15555550101",
                False,
                True,
                True,
            ),
            (
                "Harborview Psychiatric Emergency",
                "9 Harbor Ln, Metro City",
                40.7300000,
                -73.9900000,
                "+15555550102",
                True,
                False,
                False,
            ),
            (
                "Lakeside Pediatric ER",
                "55 Lake Ave, Metro City",
                40.7050000,
                -74.0200000,
                "+15555550103",
                False,
                True,
                False,
            ),
        ]
        for name, addr, lat, lng, phone, psych, ped, mat in hospitals:
            Hospital.objects.update_or_create(
                name=name,
                defaults={
                    "address": addr,
                    "location_lat": lat,
                    "location_lng": lng,
                    "phone": phone,
                    "has_psychiatric_emergency": psych,
                    "has_pediatric_emergency": ped,
                    "has_maternal_emergency": mat,
                },
            )
