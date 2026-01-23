from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('Schedule', '0008_add_shift_rotation_group'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shiftrotationgroup',
            old_name='shift_a',
            new_name='odd_shift',
        ),
        migrations.RenameField(
            model_name='shiftrotationgroup',
            old_name='shift_b',
            new_name='even_shift',
        ),
        migrations.RemoveField(
            model_name='person',
            name='rotation_order',
        ),
        migrations.RemoveField(
            model_name='person',
            name='rotation_start_month',
        ),
    ]
