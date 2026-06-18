import datetime

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def migrate_day_offs_from_hours(apps, schema_editor):
    HoursUnavailable = apps.get_model('appointment', 'HoursUnavailable')
    DayUnavailable = apps.get_model('appointment', 'DayUnavailable')

    day_offs = HoursUnavailable.objects.filter(hour=datetime.time(0, 0))
    for hu in day_offs:
        DayUnavailable.objects.get_or_create(
            user_id=hu.user_id,
            month_id=hu.month_id,
            day=hu.day,
        )
    day_offs.delete()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('appointment', '0005_remove_hoursunavailable_availability'),
    ]

    operations = [
        migrations.CreateModel(
            name='DayUnavailable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField()),
                ('month', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appointment.monthavailability')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'month', 'day')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='hoursunavailable',
            unique_together={('user', 'month', 'day', 'hour')},
        ),
        migrations.RunPython(migrate_day_offs_from_hours, migrations.RunPython.noop),
    ]
