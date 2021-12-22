# Generated by Django 3.2.9 on 2021-12-22 22:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlaylistTrackRelationship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('track_position', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='SpotifyUserPlaylistRelationship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('playlist_position', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spotify_id', models.CharField(max_length=256, unique=True)),
                ('name', models.CharField(max_length=256)),
                ('artists', models.CharField(max_length=256)),
                ('album', models.CharField(max_length=256)),
                ('features_unavailable', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='UserPlaylist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spotify_id', models.CharField(max_length=256, unique=True)),
                ('snapshot_id', models.CharField(max_length=256)),
                ('name', models.CharField(max_length=256)),
                ('owner', models.CharField(max_length=256)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('PR', 'Private'), ('PU', 'Public'), ('CO', 'Collaborative')], max_length=2)),
                ('users', models.ManyToManyField(through='music.SpotifyUserPlaylistRelationship', to='accounts.SpotifyUser')),
            ],
        ),
        migrations.CreateModel(
            name='TrackFeatures',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acousticness', models.FloatField()),
                ('danceability', models.FloatField()),
                ('energy', models.FloatField()),
                ('instrumentalness', models.FloatField()),
                ('key', models.SmallIntegerField()),
                ('liveness', models.FloatField()),
                ('loudness', models.FloatField()),
                ('mode', models.IntegerField(choices=[(1, 'Major'), (0, 'Minor')])),
                ('speechiness', models.FloatField()),
                ('tempo', models.FloatField()),
                ('time_signature', models.SmallIntegerField()),
                ('valence', models.FloatField()),
                ('track', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='track_features', to='music.track')),
            ],
        ),
        migrations.AddField(
            model_name='track',
            name='playlist',
            field=models.ManyToManyField(through='music.PlaylistTrackRelationship', to='music.UserPlaylist'),
        ),
        migrations.AddField(
            model_name='spotifyuserplaylistrelationship',
            name='playlist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='music.userplaylist'),
        ),
        migrations.AddField(
            model_name='spotifyuserplaylistrelationship',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.spotifyuser'),
        ),
        migrations.AddField(
            model_name='playlisttrackrelationship',
            name='playlist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='music.userplaylist'),
        ),
        migrations.AddField(
            model_name='playlisttrackrelationship',
            name='track',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='music.track'),
        ),
        migrations.AlterUniqueTogether(
            name='spotifyuserplaylistrelationship',
            unique_together={('user', 'playlist')},
        ),
        migrations.AlterUniqueTogether(
            name='playlisttrackrelationship',
            unique_together={('playlist', 'track')},
        ),
    ]
