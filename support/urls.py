from django.urls import path

from support.views.chat_views import ChatAPIView

from support.views.ticket_views import (
    TicketListAPIView,
    TicketDetailAPIView,
)


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
