from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIAssessmentArtifact',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('artifact_type', models.CharField(choices=[('QUIZ', 'Generated Quiz'), ('FLASHCARD', 'Flashcards'), ('SUMMARY', 'Study Summary')], default='QUIZ', max_length=20)),
                ('content', models.JSONField(help_text='Structured JSON containing generated questions or flashcard pairs')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_artifacts', to='courses.lesson')),
            ],
        ),
    ]
