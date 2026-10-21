from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import WaitingRoomEntry
from .services import join_waiting_room, leave_waiting_room


class WaitingRoomJoinView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        result, game = join_waiting_room(request.user)
        if result == 'already_waiting':
            return Response(
                {'error': 'You already have a waiting room request.'},
                status=status.HTTP_409_CONFLICT,
            )
        if result == 'ongoing_game':
            return Response(
                {'error': 'You are already in a waiting or active game.'},
                status=status.HTTP_409_CONFLICT,
            )

        response_data = {
            'queued': WaitingRoomEntry.objects.filter(user=request.user).exists(),
        }
        if game and game.players.filter(user=request.user).exists():
            response_data['game_id'] = game.pk
        return Response(response_data, status=status.HTTP_201_CREATED)


class WaitingRoomLeaveView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        leave_waiting_room(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
