# Generated by Django 3.2.4 on 2021-06-07 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stop_problem', '0004_sequenceanswer_chosen_index'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={'ordering': ['time_period']},
        ),
        migrations.AlterModelOptions(
            name='sequenceanswer',
            options={'ordering': ['sequence']},
        ),
        migrations.AlterField(
            model_name='player',
            name='gender',
            field=models.IntegerField(choices=[(1, 'Male'), (2, 'Female'), (3, 'Other'), (4, 'Rather Not Say')], default=1),
        ),
    ]
