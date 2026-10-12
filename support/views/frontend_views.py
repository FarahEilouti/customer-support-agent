from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def chat_page(request):
    return render(
        request,
        "support/chat.html",
    )
