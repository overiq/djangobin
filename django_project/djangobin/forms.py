from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from .models import Snippet, Language, Author
from .models import Snippet, Language, Author, Tag
from .utils import Preference as Pref, get_current_user
from .tasks import send_activation_mail


class SnippetForm(forms.ModelForm):

    snippet_tags = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={
                                       'class': 'selectpicker form-control',
                                       'placeholder': 'Enter tags (optional)'
                                   }))

    class Meta:
        model = Snippet
        fields = ('original_code', 'language', 'expiration', 'exposure', 'title', )
        widgets = {
            'original_code': forms.Textarea(attrs={'class': 'form-control', 'rows': '10',
                                                        'spellcheck': 'false'}),
            'language': forms.Select(attrs={'class': 'selectpicker foo form-control',
                                            'data-live-search': 'true',
                                            'data-size': '5'}),
            'expiration': forms.Select(attrs={'class': 'selectpicker form-control'}),
            'exposure': forms.Select(attrs={'class': 'selectpicker form-control'}),
            'title': forms.TextInput(attrs={'class': 'selectpicker form-control',
                                            'placeholder': 'Enter Title (optional)'}),
        }

    # override default __init__ so we can set the user preferences
    def __init__(self, request, *args, **kwargs):
        super(SnippetForm, self).__init__(*args, **kwargs)

        if request.user.is_authenticated:
            self.fields['exposure'].choices = Pref.exposure_choices
            self.initial = request.user.profile.get_preferences()
        else:
            self.fields['exposure'].choices = \
                [(k, v) for k, v in Pref.exposure_choices if k != 'private']

            l = Language.objects.get(name='Plain Text')
            self.initial = {'language': l.id, 'exposure': 'public', 'expiration': 'never'}


    def save(self, request):
        # get the Snippet object, without saving it into the database
        snippet = super(SnippetForm, self).save(commit=False)
        snippet.user = get_current_user(request)
        snippet.save()
        tag_list = [tag.strip().lower()
                   for tag in self.cleaned_data['snippet_tags'].split(',') if tag ]
        if len(tag_list) > 0:
            for tag in tag_list:
                t = Tag.objects.get_or_create(name=tag)
                snippet.tags.add(t[0])
        return snippet


class ContactForm(forms.Form):
    BUG = 'b'
    FEEDBACK = 'fb'
    NEW_FEATURE = 'nf'
    OTHER = 'o'
    purpose_choices = (
        (FEEDBACK, 'Feedback'),
        (NEW_FEATURE, 'Feature Request'),
        (BUG, 'Bug'),
        (OTHER, 'Other'),
    )

    name = forms.CharField()
    email = forms.EmailField()
    purpose = forms.ChoiceField(choices=purpose_choices)
    message = forms.CharField(widget=forms.Textarea(attrs={'cols': 40, 'rows': 5}))

    def __init__(self, request, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        if request.user.is_authenticated:
            self.fields['name'].required = False
            self.fields['email'].required = False


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            raise ValidationError("This field is required.")
        if User.objects.filter(email=self.cleaned_data['email']).count():
            raise ValidationError("Email is taken.")
        return self.cleaned_data['email']

    def save(self, request):

        user = super(CreateUserForm, self).save(commit=False)
        user.is_active = False
        user.save()

        context = {
            'protocol': request.scheme,
            'domain': request.META['HTTP_HOST'],
        }

        send_activation_mail.delay(user.id, context)  ## calling the task

        return user


class SettingForm(forms.ModelForm):

    class Meta:
        model = Author
        fields = ('default_language', 'default_expiration' , 'default_exposure' , 'private')
        widgets = {
            'default_language': forms.Select(attrs={'class': 'selectpicker foo form-control',
                                                    'data-live-search': 'true',
                                                    'data-size': '5'}),
            'default_expiration': forms.Select(attrs={'class': 'selectpicker form-control'}),
            'default_exposure': forms.Select(attrs={'class': 'selectpicker form-control'})

        }


class SearchForm(forms.Form):
    query = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                              'placeholder': 'Search'}))
    mysnippet = forms.BooleanField(required=False)
