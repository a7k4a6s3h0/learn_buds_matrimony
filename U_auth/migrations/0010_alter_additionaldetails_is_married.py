# Generated by Django 5.0.8 on 2024-08-27 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('U_auth', '0009_alter_pictures_add_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additionaldetails',
            name='is_married',
            field=models.CharField(choices=[('single', 'single'), ('married', 'married'), ('divocred', 'divocred')], max_length=50),
        ),
    ]
