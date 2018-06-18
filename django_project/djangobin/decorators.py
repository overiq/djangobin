from functools import wraps
from django.shortcuts import Http404, get_object_or_404
from django.contrib.auth import get_user_model
from .models import Language, Snippet


def private_snippet(func):
    def wrapper(request, *args, **kwargs):
        snippet = Snippet.objects.get(slug=kwargs.get('snippet_slug'))
        if snippet.exposure == 'private' and request.user != snippet.user:
            raise Http404
        return func(request, *args, **kwargs)
    return wrapper