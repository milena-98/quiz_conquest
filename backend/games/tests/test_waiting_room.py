from django.contrib.auth import get_user_model
from django.test import TestCase

from games.models import Game, GamePlayer, Round, WaitingRoomEntry
from games.services import form_waiting_room_game

User = get_user_model()


class WaitingRoomFormationTests(TestCase):
    def make_user(self, username):
        return User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='example-password',
        )

    def test_five_waiters_create_one_game_and_leave_two_requests(self):
        users = [self.make_user(f'player_{index}') for index in range(5)]
        WaitingRoomEntry.objects.bulk_create([WaitingRoomEntry(user=user) for user in users])

        old_game = Game.objects.create(created_by=users[0], status=Game.FINISHED)
        GamePlayer.objects.create(game=old_game, user=users[0], player_order=1, score=8)

        game = form_waiting_room_game()

        self.assertIsNotNone(game)
        self.assertEqual(Game.objects.count(), 2)
        game.refresh_from_db()
        self.assertEqual(game.status, Game.WAITING)
        self.assertEqual(game.players.count(), 3)
        self.assertEqual(Round.objects.filter(game=game).count(), 0)

        players = list(game.players.select_related('user').order_by('player_order'))
        selected_user_ids = {player.user_id for player in players}
        self.assertEqual(len(selected_user_ids), 3)
        self.assertTrue(selected_user_ids.issubset({user.pk for user in users}))
        self.assertEqual(game.created_by_id, players[0].user_id)
        self.assertEqual({player.player_order for player in players}, {1, 2, 3})
        self.assertEqual(len({player.color for player in players}), 3)
        self.assertTrue(all(player.color in dict(GamePlayer.COLOR_CHOICES) for player in players))
        self.assertTrue(all(player.score == 0 for player in players))

        self.assertEqual(WaitingRoomEntry.objects.count(), 2)
        self.assertEqual(
            set(WaitingRoomEntry.objects.values_list('user_id', flat=True)),
            {user.pk for user in users} - selected_user_ids,
        )
        self.assertTrue(Game.objects.filter(pk=old_game.pk, status=Game.FINISHED).exists())
        self.assertEqual(old_game.players.get().score, 8)

    def test_two_waiters_do_not_change_database(self):
        users = [self.make_user(f'player_{index}') for index in range(2)]
        WaitingRoomEntry.objects.bulk_create([WaitingRoomEntry(user=user) for user in users])
        before = {
            'entries': set(WaitingRoomEntry.objects.values_list('pk', flat=True)),
            'games': set(Game.objects.values_list('pk', flat=True)),
            'players': set(GamePlayer.objects.values_list('pk', flat=True)),
            'rounds': set(Round.objects.values_list('pk', flat=True)),
        }

        game = form_waiting_room_game()

        self.assertIsNone(game)
        self.assertEqual(set(WaitingRoomEntry.objects.values_list('pk', flat=True)), before['entries'])
        self.assertEqual(set(Game.objects.values_list('pk', flat=True)), before['games'])
        self.assertEqual(set(GamePlayer.objects.values_list('pk', flat=True)), before['players'])
        self.assertEqual(set(Round.objects.values_list('pk', flat=True)), before['rounds'])
