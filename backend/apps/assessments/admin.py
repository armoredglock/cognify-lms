from django.contrib import admin
from .models import Quiz, Question, Option, QuizAttempt, StudentAnswer


class OptionInline(admin.TabularInline):
    model = Option
    extra = 4


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'time_limit_minutes', 'passing_score', 'created_at')
    search_fields = ('title', 'lesson__title')
    list_filter = ('created_at',)
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'quiz', 'question_type', 'points')
    search_fields = ('question_text', 'quiz__title')
    list_filter = ('question_type', 'quiz')
    inlines = [OptionInline]


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('option_text', 'question', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('option_text', 'question__question_text')


class StudentAnswerInline(admin.TabularInline):
    model = StudentAnswer
    extra = 0
    readonly_fields = ('question', 'selected_option', 'answered_at')


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'total_score', 'is_passed', 'started_at', 'completed_at')
    list_filter = ('is_passed', 'started_at', 'quiz')
    search_fields = ('student__username', 'student__email', 'quiz__title')
    readonly_fields = ('started_at', 'completed_at')
    inlines = [StudentAnswerInline]


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_option', 'answered_at')
    search_fields = ('attempt__student__username', 'question__question_text')
    readonly_fields = ('answered_at',)
