# Generated by Django 2.2.1 on 2019-11-29 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_notification_itemid'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='type',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='userID',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
