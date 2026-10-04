from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Game(models.Model):
    WAITING = 'waiting'
    IN_PROGRESS = 'in_progress'
    FINISHED = 'finished'
    CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (WAITING, 'Waiting'),
        (IN_PROGRESS, 'In Progress'),
        (FINISHED, 'Finished'),
        (CANCELLED, 'Cancelled'),
    ]

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_games',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Game #{self.pk} by {self.created_by}'


class GamePlayer(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='players')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='game_players',
    )
    player_order = models.PositiveSmallIntegerField()
    score = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['game', 'user'], name='unique_game_player_per_game'),
            models.UniqueConstraint(fields=['game', 'player_order'], name='unique_game_player_order'),
        ]
        ordering = ['game__id', 'player_order']

    def clean(self):
        super().clean()
        if self.player_order <= 0:
            raise ValidationError({'player_order': 'Player order must be greater than zero.'})

    def __str__(self):
        return f'{self.user} in Game #{self.game_id}'


class Round(models.Model):
    PENDING = 'pending'
    OPEN = 'open'
    CLOSED = 'closed'
    EVALUATED = 'evaluated'

    ROUND_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (OPEN, 'Open'),
        (CLOSED, 'Closed'),
        (EVALUATED, 'Evaluated'),
    ]

    CHOICE = 'choice'
    NUMERIC = 'numeric'

    QUESTION_TYPE_CHOICES = [
        (CHOICE, 'Choice'),
        (NUMERIC, 'Numeric'),
    ]

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='rounds')
    number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=ROUND_STATUS_CHOICES)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    choice_question = models.ForeignKey(
        'questions.ChoiceQuestion',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='rounds_as_choice',
    )
    numeric_question = models.ForeignKey(
        'questions.NumericQuestion',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='rounds_as_numeric',
    )
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['game', 'number'], name='unique_round_number_per_game'),
        ]
        ordering = ['game__id', 'number']

    def clean(self):
        super().clean()
        if self.number <= 0:
            raise ValidationError({'number': 'Round number must be greater than zero.'})

        if self.question_type == self.CHOICE:
            if not self.choice_question_id:
                raise ValidationError({'choice_question': 'Choice question is required for choice rounds.'})
            if self.numeric_question_id:
                raise ValidationError({'numeric_question': 'Numeric question must be empty for choice rounds.'})
        elif self.question_type == self.NUMERIC:
            if not self.numeric_question_id:
                raise ValidationError({'numeric_question': 'Numeric question is required for numeric rounds.'})
            if self.choice_question_id:
                raise ValidationError({'choice_question': 'Choice question must be empty for numeric rounds.'})
        else:
            raise ValidationError({'question_type': 'Invalid question type.'})

    def __str__(self):
        return f'Round {self.number} for Game #{self.game_id}'


class RoundAnswer(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='answers')
    player = models.ForeignKey(
        GamePlayer,
        on_delete=models.CASCADE,
        related_name='round_answers',
    )
    selected_option = models.ForeignKey(
        'questions.AnswerOption',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='selected_in_answers',
    )
    numeric_value = models.IntegerField(null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    points_awarded = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['round', 'player'], name='unique_round_answer_per_player'),
        ]
        ordering = ['round__game__id', 'round__number', 'player__player_order']

    def clean(self):
        super().clean()
        if self.round_id and self.player_id and self.round.game_id != self.player.game_id:
            raise ValidationError('The player must belong to the same game as the round.')

        if self.round_id and self.round.question_type == Round.CHOICE:
            if self.selected_option_id is None:
                raise ValidationError({'selected_option': 'Selected option is required for choice rounds.'})
            if self.numeric_value is not None:
                raise ValidationError({'numeric_value': 'Numeric value must be empty for choice rounds.'})
            if self.round.choice_question_id and self.selected_option_id and self.selected_option.question_id != self.round.choice_question_id:
                raise ValidationError({'selected_option': 'Selected option must belong to the round question.'})
        elif self.round_id and self.round.question_type == Round.NUMERIC:
            if self.numeric_value is None:
                raise ValidationError({'numeric_value': 'Numeric value is required for numeric rounds.'})
            if self.selected_option_id is not None:
                raise ValidationError({'selected_option': 'Selected option must be empty for numeric rounds.'})

    def __str__(self):
        return f'{self.player} answer for Round {self.round.number}'
