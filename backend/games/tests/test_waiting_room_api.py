from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from games.models import Game, GamePlayer, WaitingRoomEntry

User = get_user_model()


class WaitingRoomApiTests(TestCase):
    def make_user(self, username):
        return User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='example-password',
        )

    def test_join_rejects_repeat_and_leave_is_idempotent(self):
        user = self.make_user('player')
        other_user = self.make_user('other')
        WaitingRoomEntry.objects.create(user=other_user)
        self.client.force_login(user)

        self.assertEqual(self.client.post(reverse('waiting-room-join')).status_code, 201)
        self.assertEqual(self.client.post(reverse('waiting-room-join')).status_code, 409)
        self.assertEqual(WaitingRoomEntry.objects.filter(user=user).count(), 1)

        self.assertEqual(self.client.delete(reverse('waiting-room-leave')).status_code, 204)
        self.assertFalse(WaitingRoomEntry.objects.filter(user=user).exists())
        self.assertEqual(self.client.delete(reverse('waiting-room-leave')).status_code, 204)
        self.assertTrue(WaitingRoomEntry.objects.filter(user=other_user).exists())

    def test_waiting_and_active_game_block_join_but_finished_game_does_not(self):
        busy_users = [self.make_user('waiting'), self.make_user('active')]
        completed_user = self.make_user('completed')
        for user, game_status in zip(busy_users, (Game.WAITING, Game.IN_PROGRESS)):
            game = Game.objects.create(created_by=user, status=game_status)
            GamePlayer.objects.create(game=game, user=user, player_order=1)
        finished_game = Game.objects.create(created_by=completed_user, status=Game.FINISHED)
        GamePlayer.objects.create(game=finished_game, user=completed_user, player_order=1)

        for user in busy_users:
            self.client.force_login(user)
            self.assertEqual(self.client.post(reverse('waiting-room-join')).status_code, 409)
            self.assertFalse(WaitingRoomEntry.objects.filter(user=user).exists())

        self.client.force_login(completed_user)
        self.assertEqual(self.client.post(reverse('waiting-room-join')).status_code, 201)
        self.assertTrue(WaitingRoomEntry.objects.filter(user=completed_user).exists())
