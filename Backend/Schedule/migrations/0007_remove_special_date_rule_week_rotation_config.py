from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('Schedule', '0006_alter_calendaroverride_target'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SpecialDateRule',
        ),
        migrations.DeleteModel(
            name='WeekRotationConfig',
        ),
    ]
