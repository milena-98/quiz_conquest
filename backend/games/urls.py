from django.urls import path

from .views import WaitingRoomJoinView, WaitingRoomLeaveView

urlpatterns = [
    path('waiting-room/join/', WaitingRoomJoinView.as_view(), name='waiting-room-join'),
    path('waiting-room/leave/', WaitingRoomLeaveView.as_view(), name='waiting-room-leave'),
]
