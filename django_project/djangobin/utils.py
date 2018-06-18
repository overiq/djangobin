from django.contrib.auth.models import User
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger


class Preference:

    SNIPPET_EXPIRE_NEVER = 'never'
    SNIPPET_EXPIRE_1WEEK = '1 week'
    SNIPPET_EXPIRE_1MONTH = '1 month'
    SNIPPET_EXPIRE_6MONTH = '6 month'
    SNIPPET_EXPIRE_1YEAR = '1 year'

    expiration_choices = (
        (SNIPPET_EXPIRE_NEVER, 'Never'),
        (SNIPPET_EXPIRE_1WEEK, '1 week'),
        (SNIPPET_EXPIRE_1MONTH, '1 month'),
        (SNIPPET_EXPIRE_6MONTH, '6 month'),
        (SNIPPET_EXPIRE_1YEAR, '1 year'),
    )

    SNIPPET_EXPOSURE_PUBLIC = 'public'
    SNIPPET_EXPOSURE_UNLIST = 'unlisted'
    SNIPPET_EXPOSURE_PRIVATE = 'private'

    exposure_choices = (
        (SNIPPET_EXPOSURE_PUBLIC, 'Public'),
        (SNIPPET_EXPOSURE_UNLIST, 'Unlisted'),
        (SNIPPET_EXPOSURE_PRIVATE, 'Private'),
    )


def get_current_user(request):
    if request.user.is_authenticated:
        return request.user
    else:
       return User.objects.filter(username='guest')[0]


def paginate_result(request, object_list, item_per_page):
    paginator = Paginator(object_list, item_per_page)

    page = request.GET.get('page')

    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        results = paginator.page(paginator.num_pages)

    return results