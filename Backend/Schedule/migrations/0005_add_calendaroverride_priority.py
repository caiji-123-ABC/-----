from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('Schedule', '0004_remove_personoverride'),
    ]

    operations = [
        migrations.AddField(
            model_name='calendaroverride',
            name='priority',
            field=models.IntegerField(default=0, verbose_name='优先级'),
        ),
    ]
