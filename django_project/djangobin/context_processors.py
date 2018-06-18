from .models import Snippet


def recent_snippets(request):
    return dict(recent_snippets=Snippet.objects.filter(exposure='public').order_by("-id")[:8])