# Generated by Django 3.2.9 on 2021-12-09 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0005_auto_20211209_1332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userplaylist',
            name='owner',
            field=models.CharField(default='', max_length=256),
            preserve_default=False,
        ),
    ]
