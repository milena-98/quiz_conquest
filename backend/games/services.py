from django.db import transaction

from .models import Game, GamePlayer, WaitingRoomEntry


def user_has_ongoing_game(user):
    return GamePlayer.objects.filter(
        user=user,
        game__status__in=(Game.WAITING, Game.IN_PROGRESS),
    ).exists()


def join_waiting_room(user):
    if WaitingRoomEntry.objects.filter(user=user).exists():
        return 'already_waiting', None
    if user_has_ongoing_game(user):
        return 'ongoing_game', None

    WaitingRoomEntry.objects.create(user=user)
    return 'joined', form_waiting_room_game()


def leave_waiting_room(user):
    WaitingRoomEntry.objects.filter(user=user).delete()


@transaction.atomic
def form_waiting_room_game():
    ongoing_users = GamePlayer.objects.filter(
        game__status__in=(Game.WAITING, Game.IN_PROGRESS),
    ).values_list('user_id', flat=True)
    selected_entries = list(
        WaitingRoomEntry.objects.exclude(user_id__in=ongoing_users)
        .select_related('user')
        .order_by('?')[:3]
    )
    if len(selected_entries) < 3:
        return None

    game = Game.objects.create(
        created_by=selected_entries[0].user,
        status=Game.WAITING,
    )
    colors = (GamePlayer.RED, GamePlayer.BLUE, GamePlayer.GREEN)
    GamePlayer.objects.bulk_create([
        GamePlayer(
            game=game,
            user=entry.user,
            player_order=order,
            color=colors[order - 1],
            score=0,
        )
        for order, entry in enumerate(selected_entries, start=1)
    ])
    WaitingRoomEntry.objects.filter(pk__in=[entry.pk for entry in selected_entries]).delete()
    return game
