from django.urls import path

from support.views.chat_views import ChatAPIView


urlpatterns = [
    path("chat/", ChatAPIView.as_view(), name="chat"),
]