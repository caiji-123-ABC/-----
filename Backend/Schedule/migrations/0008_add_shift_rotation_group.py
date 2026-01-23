from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('Schedule', '0007_remove_special_date_rule_week_rotation_config'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShiftRotationGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('remark', models.TextField(blank=True, null=True)),
                ('shift_a', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rotation_group_a', to='Schedule.shiftdefinition', verbose_name='轮换班次A')),
                ('shift_b', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rotation_group_b', to='Schedule.shiftdefinition', verbose_name='轮换班次B')),
            ],
            options={
                'db_table': 'shift_rotation_group',
            },
        ),
        migrations.AddField(
            model_name='person',
            name='rotation_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Schedule.shiftrotationgroup'),
        ),
        migrations.AddField(
            model_name='person',
            name='rotation_order',
            field=models.CharField(choices=[('AB', '本月A下月B'), ('BA', '本月B下月A')], default='AB', max_length=2),
        ),
        migrations.AddField(
            model_name='person',
            name='rotation_start_month',
            field=models.CharField(blank=True, max_length=7, null=True, verbose_name='起始月份YYYY-MM'),
        ),
    ]
