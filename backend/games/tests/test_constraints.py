from django.db import IntegrityError
from django.test import TestCase

from accounts.models import User
from games.models import Game, GamePlayer, Round
from questions.models import Category


class GameConstraintsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='gamma', email='gamma@example.com', password='secret123')
        self.category = Category.objects.create(name='Geography')

    def test_unique_player_order_per_game(self):
        game = Game.objects.create(created_by=self.user)
        GamePlayer.objects.create(game=game, user=self.user, player_order=1)

        with self.assertRaises(IntegrityError):
            GamePlayer.objects.create(
                game=game,
                user=User.objects.create_user(username='delta', email='delta@example.com', password='secret123'),
                player_order=1,
            )

    def test_unique_round_number_per_game(self):
        game = Game.objects.create(created_by=self.user)
        Round.objects.create(game=game, number=1, question_type=Round.CHOICE)

        with self.assertRaises(IntegrityError):
            Round.objects.create(game=game, number=1, question_type=Round.NUMERIC)
