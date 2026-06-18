from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0006_dayunavailable_and_unique_constraints'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pendente'),
                    ('confirmed', 'Confirmado'),
                    ('rejected', 'Recusado'),
                ],
                default='confirmed',
                max_length=10,
            ),
        ),
    ]
