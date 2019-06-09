# Generated by Django 2.1.5 on 2019-02-19 19:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TravelDestination',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pincode', models.PositiveIntegerField()),
                ('city', models.CharField(choices=[(None, '---- Please choose city ----'), ('vasco', 'Vasco'), ('margao', 'Margao')], max_length=45)),
                ('lon', models.FloatField(verbose_name='Longitude')),
                ('lat', models.FloatField(verbose_name='latitude')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='traveldestination_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
