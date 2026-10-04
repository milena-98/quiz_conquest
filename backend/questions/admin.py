from django.contrib import admin

from .models import AnswerOption, Category, ChoiceQuestion, NumericQuestion


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 4
    fields = ('text', 'is_correct')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(ChoiceQuestion)
class ChoiceQuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerOptionInline]
    list_display = ('text', 'category')
    list_filter = ('category',)
    search_fields = ('text',)


@admin.register(NumericQuestion)
class NumericQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'category', 'correct_answer')
    list_filter = ('category',)
    search_fields = ('text',)
