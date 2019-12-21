# Generated by Django 2.2.7 on 2019-12-17 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stes_test', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='results',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=40)),
                ('physics_marks', models.IntegerField(default=0)),
                ('chemistry_marks', models.IntegerField(default=0)),
                ('math_marks', models.IntegerField(default=0)),
                ('total_marks', models.IntegerField(default=0)),
            ],
        ),
    ]
