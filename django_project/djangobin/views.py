from django.shortcuts import HttpResponse, render, redirect, get_object_or_404, reverse, \
    get_list_or_404, Http404
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.mail import mail_admins
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
import datetime
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import SnippetForm, ContactForm, LoginForm, CreateUserForm, SettingForm, SearchForm
from .models import Language, Snippet, Tag
from .utils import paginate_result
from .decorators import private_snippet
from .tasks import send_feedback_mail


def index(request):
    if request.method ==  'POST':
        f = SnippetForm(request, request.POST)

        if f.is_valid():
            snippet = f.save(request)
            return redirect(reverse('djangobin:snippet_detail', args=[snippet.slug]))

    else:
        f = SnippetForm(request)
    return render(request, 'djangobin/index.html', {'form': f})


@private_snippet
def snippet_detail(request, snippet_slug):
    snippet = get_object_or_404(Snippet, slug=snippet_slug)
    snippet.hits += 1
    snippet.save()
    return render(request, 'djangobin/snippet_detail.html', {'snippet': snippet})


@private_snippet
def download_snippet(request, snippet_slug):
    snippet = get_object_or_404(Snippet, slug=snippet_slug)
    file_extension = snippet.language.file_extension
    filename = snippet.slug + file_extension
    res = HttpResponse(snippet.original_code)
    res['content-disposition'] = 'attachment; filename=' + filename + ";"
    return res


@private_snippet
def raw_snippet(request, snippet_slug):
    snippet = get_object_or_404(Snippet, slug=snippet_slug)
    return HttpResponse(snippet.original_code, content_type=snippet.language.mime)


def trending_snippets(request, language_slug=''):
    lang = None
    snippets = Snippet.objects
    if language_slug:
        snippets = snippets.filter(language__slug=language_slug)
        lang = get_object_or_404(Language, slug=language_slug)

    snippet_list = get_list_or_404(snippets.filter(exposure='public').order_by('-hits'))
    snippets = paginate_result(request, snippet_list, 5)

    return render(request, 'djangobin/trending.html', {'snippets': snippets, 'lang': lang})


def contact(request):
    if request.method == 'POST':
        f = ContactForm(request, request.POST)
        if f.is_valid():

            if request.user.is_authenticated:
                name = request.user.username
                email = request.user.email
            else:
                name = f.cleaned_data['name']
                email = f.cleaned_data['email']

            subject = "You have a new Feedback from {}:<{}>".format(name, email)

            message = "Purpose: {}\n\nDate: {}\n\nMessage:\n\n {}".format(
                dict(f.purpose_choices).get(f.cleaned_data['purpose']),
                datetime.datetime.now(),
                f.cleaned_data['message']
            )

            send_feedback_mail.delay(subject, message)

            messages.add_message(request, messages.INFO, 'Thanks for submitting your feedback.')

            return redirect('djangobin:contact')

    else:
        f = ContactForm(request)

    return render(request, 'djangobin/contact.html', {'form': f})


def tag_list(request, tag):
    t = get_object_or_404(Tag, name=tag)
    snippet_list = get_list_or_404(t.snippet_set)
    snippets = paginate_result(request, snippet_list, 5)
    return render(request, 'djangobin/tag_list.html', {'snippets': snippets, 'tag': t})


def profile(request, username):
    user = get_object_or_404(User, username=username)

    # if the profile is private and logged in user is not same as the user being viewed,
    # show 404 error
    if user.profile.private and request.user.username != user.username:
        raise Http404

    # if the profile is not private and logged in user is not same as the user being viewed,
    # then only show public snippets of the user
    elif not user.profile.private and request.user.username != user.username:
        snippet_list = user.snippet_set.filter(exposure='public')
        user.profile.views += 1
        user.profile.save()

    # logged in user is same as the user being viewed
    # show everything
    else:
        snippet_list = user.snippet_set.all()

    snippets = paginate_result(request, snippet_list, 5)

    return render(request, 'djangobin/profile.html',
                  {'user' : user, 'snippets' : snippets } )


def search(request):
    f = SearchForm(request.GET)
    snippets = []

    if f.is_valid():

        query = f.cleaned_data.get('query')
        mysnippets = f.cleaned_data.get('mysnippet')

        # if mysnippet field is selected, search only logged in user's snippets
        if mysnippets:
            snippet_list = Snippet.objects.filter(
                Q(user=request.user),
                Q(original_code__icontains=query) | Q(title__icontains=query)
            )

        else:
            qs1 = Snippet.objects.filter(
                Q(exposure='public'),
                Q(original_code__icontains = query) | Q(title__icontains = query)
                # Q(user=request.user)
            )

            # if the user is logged in then search his snippets
            if request.user.is_authenticated:
               qs2 = Snippet.objects.filter(Q(user=request.user),
                                            Q(original_code__icontains=query) | Q(title__icontains=query))
               snippet_list = (qs1 | qs2).distinct()

            else:
                snippet_list = qs1

        snippets = paginate_result(request, snippet_list, 5)

    return render(request, 'djangobin/search.html', {'form': f, 'snippets': snippets })


@login_required
def delete_snippet(request, snippet_slug):
    snippet = get_object_or_404(Snippet, slug=snippet_slug)
    if not snippet.user == request.user:
        raise Http404
    snippet.delete()
    return redirect('djangobin:profile', request.user)


def login(request):

    if request.user.is_authenticated:
        return redirect('djangobin:profile', username=request.user.username)

    if request.method == 'POST':

        f = LoginForm(request.POST)
        if f.is_valid():

            user = User.objects.filter(email=f.cleaned_data['email'])

            if user:
                user = auth.authenticate(
                    username=user[0].username,
                    password=f.cleaned_data['password'],
                )

                if user:
                    auth.login(request, user)
                    return redirect( request.GET.get('next') or 'djangobin:index' )

            messages.add_message(request, messages.INFO, 'Invalid email/password.')
            return redirect('djangobin:login')

    else:
        f = LoginForm()

    return render(request, 'djangobin/login.html', {'form': f})


def signup(request):
    if request.method == 'POST':
        f = CreateUserForm(request.POST)
        if f.is_valid():
            f.save(request)
            messages.success(request, 'Account created successfully. Check email to verify the account.')
            return redirect('djangobin:signup')

    else:
        f = CreateUserForm()

    return render(request, 'djangobin/signup.html', {'form': f})


def activate_account(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if (user is not None and default_token_generator.check_token(user, token)):
        user.is_active = True
        user.save()
        messages.add_message(request, messages.INFO, 'Account activated. Please login.')
    else:
        messages.add_message(request, messages.INFO, 'Link Expired. Contact admin to activate your account.')

    return redirect('djangobin:login')


@login_required
def settings(request):
    user = get_object_or_404(User, id=request.user.id)
    if request.method == 'POST':
        f = SettingForm(request.POST, instance=user.profile)
        if f.is_valid():
            f.save()
            messages.add_message(request, messages.INFO, 'Settings Saved.')
            return redirect(reverse('djangobin:settings'))

    else:
        f = SettingForm(instance=user.profile)

    return render(request, 'djangobin/settings.html', {'form': f})


@login_required
def logout(request):
    auth.logout(request)
    return render(request,'djangobin/logout.html')


@login_required
def user_details(request):
    user = get_object_or_404(User, id=request.user.id)
    return render(request, 'djangobin/user_details.html', {'user': user})
