# Generated by Django 3.2.6 on 2021-08-20 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0008_alter_video_video_embed_id'),
        ('playlists', '0002_playlist_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='videos',
            field=models.ManyToManyField(blank=True, related_name='playlist_item', to='videos.Video'),
        ),
    ]
