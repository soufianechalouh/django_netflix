# Generated by Django 3.2.6 on 2021-08-20 17:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('playlists', '0008_auto_20210820_1712'),
    ]

    operations = [
        migrations.CreateModel(
            name='MovieProxy',
            fields=[
            ],
            options={
                'verbose_name': 'Movie',
                'verbose_name_plural': 'Movies',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('playlists.playlist',),
        ),
    ]
