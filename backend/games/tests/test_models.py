from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import User
from games.models import Game, GamePlayer, Round, RoundAnswer
from questions.models import AnswerOption, Category, ChoiceQuestion, NumericQuestion


class GameModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alpha', email='alpha@example.com', password='secret123')
        self.category = Category.objects.create(name='Science')

    def test_game_and_players_are_created(self):
        game = Game.objects.create(created_by=self.user, status=Game.WAITING)
        GamePlayer.objects.create(game=game, user=self.user, player_order=1)

        self.assertEqual(game.players.count(), 1)
        self.assertEqual(game.players.first().user, self.user)

    def test_round_requires_correct_question_type_data(self):
        game = Game.objects.create(created_by=self.user, status=Game.WAITING)
        choice_question = ChoiceQuestion.objects.create(category=self.category, text='Which planet is known as the Red Planet?')
        for idx, option in enumerate(['Mars', 'Venus', 'Jupiter', 'Earth']):
            AnswerOption.objects.create(question=choice_question, text=option, is_correct=(idx == 0))

        round_obj = Round(game=game, number=1, status=Round.PENDING, question_type=Round.CHOICE, choice_question=choice_question)
        round_obj.full_clean()

        with self.assertRaises(ValidationError):
            Round(game=game, number=2, question_type=Round.CHOICE).full_clean()

    def test_round_answer_validates_player_game_match(self):
        game = Game.objects.create(created_by=self.user, status=Game.WAITING)
        other_user = User.objects.create_user(username='beta', email='beta@example.com', password='secret123')
        other_game = Game.objects.create(created_by=other_user, status=Game.WAITING)
        player = GamePlayer.objects.create(game=game, user=self.user, player_order=1)
        other_player = GamePlayer.objects.create(game=other_game, user=other_user, player_order=1)

        round_obj = Round.objects.create(
            game=game,
            number=1,
            question_type=Round.NUMERIC,
            numeric_question=NumericQuestion.objects.create(
                category=self.category,
                text='What is 2 + 2?',
                correct_answer=4,
            ),
        )

        answer = RoundAnswer(round=round_obj, player=other_player, numeric_value=3)
        with self.assertRaises(ValidationError):
            answer.full_clean()

        valid_answer = RoundAnswer(round=round_obj, player=player, numeric_value=4)
        valid_answer.full_clean()
        self.assertEqual(valid_answer.points_awarded, 0)
