from django.contrib import admin

from .models import Game, GamePlayer, Round, RoundAnswer


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_by', 'status', 'created_at', 'started_at', 'finished_at')
    list_filter = ('status', 'created_by')
    search_fields = ('created_by__username',)


@admin.register(GamePlayer)
class GamePlayerAdmin(admin.ModelAdmin):
    list_display = ('game', 'user', 'player_order', 'score', 'is_active')
    list_filter = ('game', 'is_active')
    search_fields = ('user__username',)


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ('game', 'number', 'status', 'question_type', 'choice_question', 'numeric_question')
    list_filter = ('status', 'question_type', 'game')
    search_fields = ('game__created_by__username',)


@admin.register(RoundAnswer)
class RoundAnswerAdmin(admin.ModelAdmin):
    list_display = ('round', 'player', 'selected_option', 'numeric_value', 'is_correct', 'points_awarded')
    list_filter = ('round__game', 'is_correct')
    search_fields = ('player__user__username',)
