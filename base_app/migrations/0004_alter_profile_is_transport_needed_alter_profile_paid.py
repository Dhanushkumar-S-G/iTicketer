# Generated by Django 4.2.9 on 2024-01-02 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0003_profile_jnm_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='is_transport_needed',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='paid',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
