# Generated by Django 3.2.9 on 2021-12-07 16:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Track",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("spotify_id", models.CharField(max_length=256)),
                ("name", models.CharField(max_length=256)),
                ("artists", models.CharField(max_length=256)),
                ("album", models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name="UserPlaylist",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("spotify_id", models.CharField(max_length=256)),
                ("snapshot_id", models.CharField(max_length=256)),
                ("name", models.CharField(max_length=256)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.spotifyuser",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TrackFeatures",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("acousticness", models.FloatField()),
                ("danceability", models.FloatField()),
                ("energy", models.FloatField()),
                ("instrumentalness", models.FloatField()),
                ("key", models.SmallIntegerField()),
                ("liveness", models.FloatField()),
                ("loudness", models.FloatField()),
                ("mode", models.IntegerField(choices=[(1, "Major"), (0, "Minor")])),
                ("speechiness", models.FloatField()),
                ("tempo", models.FloatField()),
                ("time_signature", models.SmallIntegerField()),
                ("valence", models.FloatField()),
                (
                    "track",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="track_features",
                        to="music.track",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="track",
            name="playlist",
            field=models.ManyToManyField(to="music.UserPlaylist"),
        ),
    ]