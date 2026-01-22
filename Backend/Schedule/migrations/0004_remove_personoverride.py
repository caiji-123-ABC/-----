from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('Schedule', '0003_delete_globalrules'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PersonOverride',
        ),
    ]
