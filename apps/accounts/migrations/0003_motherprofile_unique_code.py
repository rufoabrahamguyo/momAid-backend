# Generated manually for partner pairing

import secrets
import string

from django.db import migrations, models


def assign_unique_codes(apps, schema_editor):
    MotherProfile = apps.get_model("accounts", "MotherProfile")
    alphabet = string.ascii_uppercase + string.digits
    for mp in MotherProfile.objects.filter(unique_code__isnull=True):
        for _ in range(512):
            code = "".join(secrets.choice(alphabet) for _ in range(8))
            qs = MotherProfile.objects.filter(unique_code=code).exclude(pk=mp.pk)
            if not qs.exists():
                mp.unique_code = code
                mp.save(update_fields=["unique_code"])
                break


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_user_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="motherprofile",
            name="unique_code",
            field=models.CharField(blank=True, db_index=True, editable=False, help_text="Share this code with your partner to link accounts.", max_length=32, null=True, unique=True),
        ),
        migrations.RunPython(assign_unique_codes, noop_reverse),
        migrations.AlterField(
            model_name="motherprofile",
            name="unique_code",
            field=models.CharField(db_index=True, editable=False, help_text="Share this code with your partner to link accounts.", max_length=32, unique=True),
        ),
    ]
