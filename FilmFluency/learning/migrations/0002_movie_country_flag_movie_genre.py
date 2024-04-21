from django.db import migrations, models
from django.db import connection

class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='country_flag',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.RunSQL(
            "ALTER TABLE learning_movie ADD COLUMN IF NOT EXISTS genre VARCHAR(100) DEFAULT '28';",
            reverse_sql="ALTER TABLE learning_movie DROP COLUMN genre;",
        ),
    ]
