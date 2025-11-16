from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drivingschool', '0009_review_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='student',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='review',
            name='instructor',
            field=models.CharField(max_length=100),
        ),
    ]