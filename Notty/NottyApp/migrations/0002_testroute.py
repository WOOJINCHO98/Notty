# Generated by Django 4.0.6 on 2022-07-20 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NottyApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='testRoute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.CharField(max_length=30)),
                ('fin', models.CharField(max_length=30)),
            ],
        ),
    ]
