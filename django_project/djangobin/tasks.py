from celery import task
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.mail import BadHeaderError, send_mail, mail_admins
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
import datetime, pytz
from .models import Snippet
from .utils import Preference as Pref


@task
def send_activation_mail(user_id, context):

    user = User.objects.get(id=user_id)

    context.update({
        'username': user.username,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })

    subject = render_to_string('djangobin/email/activation_subject.txt', context)
    email = render_to_string('djangobin/email/activation_email.txt', context)

    send_mail(subject, email, settings.DEFAULT_FROM_EMAIL, [user.email])


@task
def send_feedback_mail(subject, message):
    mail_admins(subject, message)


@task
def remove_snippets():

    # loop through all the snippets whose expiration is other than never.
    for s in Snippet.objects.exclude(expiration='never').order_by('id'):

        # get the creation time
        creation_time = s.created_on

        if s.expiration == Pref.SNIPPET_EXPIRE_1WEEK:
            tmdelta =  datetime.timedelta(days=7)
        elif s.expiration == Pref.SNIPPET_EXPIRE_1MONTH:
            tmdelta =  datetime.timedelta(days=30)
        elif s.expiration == Pref.SNIPPET_EXPIRE_6MONTH:
            tmdelta = datetime.timedelta(days=30*6)
        elif s.expiration == Pref.SNIPPET_EXPIRE_1YEAR:
            tmdelta = datetime.timedelta(days=30*12)

        # deletion_time is datetime.datetime
        deletion_time = creation_time + tmdelta

        # now is datetime.datetime
        now = datetime.datetime.now(pytz.utc)

        # diff is datetime.timedelta
        diff = deletion_time - now

        if diff.days == 0 or diff.days < 0:
            # it's time to delete the snippet
            s.delete()
