from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('time_limit_minutes', models.PositiveIntegerField(default=15, help_text='Duration in minutes managed via Redis TTL')),
                ('passing_score', models.PositiveIntegerField(default=70, help_text='Minimum passing percentage')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('lesson', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='quiz', to='courses.lesson')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('question_text', models.TextField()),
                ('question_type', models.CharField(choices=[('MCQ', 'Multiple Choice'), ('TRUE_FALSE', 'True / False')], default='MCQ', max_length=20)),
                ('points', models.PositiveIntegerField(default=1)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='assessments.quiz')),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('option_text', models.CharField(max_length=500)),
                ('is_correct', models.BooleanField(default=False)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='assessments.question')),
            ],
        ),
        migrations.CreateModel(
            name='QuizAttempt',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('total_score', models.IntegerField(default=0)),
                ('is_passed', models.BooleanField(default=False)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attempts', to='assessments.quiz')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quiz_attempts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StudentAnswer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('attempt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_answers', to='assessments.quizattempt')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assessments.question')),
                ('selected_option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assessments.option')),
            ],
            options={
                'unique_together': {('attempt', 'question')},
            },
        ),
    ]
