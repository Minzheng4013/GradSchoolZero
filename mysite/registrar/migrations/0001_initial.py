# Generated by Django 3.2.7 on 2021-11-14 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProcessInstructorComplaint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_investigated', models.BooleanField(default=False)),
                ('action', models.CharField(choices=[('ws', 'warn the student'), ('ds', 'de-register the student'), ('wi', 'warn the instructor')], default='ws', max_length=50)),
                ('person_id', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ProcessStudentComplaint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_investigated', models.BooleanField(default=False)),
                ('action', models.CharField(choices=[('ws', 'warn the student'), ('wi', 'warn the instructor')], default='ws', max_length=50)),
                ('person_id', models.PositiveIntegerField()),
            ],
        ),
    ]
