import uuid
from django.db import migrations, models

def populate_anonymous_ids(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    # Use standard ORM or native SQL logic to populate unique entries
    for user in User.objects.filter(anonymous_id__isnull=True):
        user.anonymous_id = uuid.uuid4()
        user.save(update_fields=['anonymous_id'])

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_motherprofile_options_and_more'),
    ]

    operations = [
        # 1. Add the field allowing null temporarily, so Django knows about it!
        migrations.AddField(
            model_name='user',
            name='anonymous_id',
            field=models.UUIDField(null=True, blank=True, editable=False),
        ),
        # 2. Backfill existing records
        migrations.RunPython(populate_anonymous_ids, reverse_code=migrations.RunPython.noop),
        # 3. Alter it to be unique and non-nullable now that all fields have data
        migrations.AlterField(
            model_name='user',
            name='anonymous_id',
            field=models.UUIDField(db_index=True, editable=False, unique=True, default=uuid.uuid4),
        ),
        # 4. Add your new nickname field here too if you want to keep them bundled!
        migrations.AddField(
            model_name='user',
            name='nickname',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]