from django.urls import path

from support.views.chat.chat_view import ChatAPIView

from support.views.support.ticket_list_view import TicketListAPIView
from support.views.support.ticket_detail_view import TicketDetailAPIView


urlpatterns = [
    path(
        "chat/",
        ChatAPIView.as_view(),
        name="chat",
    ),

    path(
        "tickets/",
        TicketListAPIView.as_view(),
        name="ticket-list",
    ),
    
    path(
        "tickets/<int:ticket_id>/",
        TicketDetailAPIView.as_view(),
        name="ticket-detail",
    ),
]
