# Generated by Django 5.0.8 on 2024-10-05 16:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('U_auth', '0030_remove_partnerpreference_interests_hobbies_and_more'),
        ('U_messages', '0007_alter_notificationdetails_image'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationdetails',
            name='targeted_audiences',
            field=models.CharField(choices=[('id', 'id'), ('selected', 'selected'), ('location', 'location')], max_length=20),
        ),
        migrations.CreateModel(
            name='AmidUsers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('locations', models.ManyToManyField(to='U_auth.userpersonaldetails')),
                ('notification_obj', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='amid_users', to='U_messages.notificationdetails')),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
