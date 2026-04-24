# Generated manually for User.avatar (profile photo upload)

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="avatar",
            field=models.ImageField(
                blank=True,
                help_text="Profile photo (mobile clients: PATCH profile as multipart/form-data with photo file).",
                null=True,
                upload_to="avatars/%Y/%m/",
            ),
        ),
    ]
