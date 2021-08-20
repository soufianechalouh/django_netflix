# Generated by Django 3.2.6 on 2021-08-20 11:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('playlists', '0005_playlist_videos'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='order',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='playlist',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='playlists.playlist'),
        ),
    ]