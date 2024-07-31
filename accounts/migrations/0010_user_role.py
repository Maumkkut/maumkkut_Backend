# Generated by Django 5.0.6 on 2024-07-31 03:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_user_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('group_leader', 'Group Leader'), ('group_member', 'Group Member')], default='group_member', max_length=20),
        ),
    ]