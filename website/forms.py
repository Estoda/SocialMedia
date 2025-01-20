from django.contrib.auth.forms import UserCreationForm
from .models import User, Post, Comment
from django import forms
from django.core.exceptions import ValidationError
from PIL import Image


class PostForm(forms.ModelForm):
    content = forms.CharField(
        label="",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "style": "resize: none;",
                "placeholder": "What 's on your mind?",
            }
        ),
    )
    file = forms.FileField(
        label="Photo",
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control-file"}),
    )

    class Meta:
        model = Post
        fields = (
            "content",
            "file",
        )


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        label="",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Email Address"}
        ),
    )
    first_name = forms.CharField(
        label="",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "First Name"}
        ),
    )
    last_name = forms.CharField(
        label="",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Last Name"}
        ),
    )
    profile_picture = forms.ImageField(
        label="Profile Photo",
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control-file"}),
    )
    bio = forms.CharField(
        label="",
        required=False,
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "Bio", "rows": 3}
        ),
    )
    location = forms.CharField(
        label="",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Location"}
        ),
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            "profile_picture",
            "bio",
            "location",
        )

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields["username"].widget.attrs["class"] = "form-control"
        self.fields["username"].widget.attrs["placeholder"] = "User Name"
        self.fields["username"].label = ""
        self.fields["username"].help_text = (
            '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'
        )

        self.fields["password1"].widget.attrs["class"] = "form-control"
        self.fields["password1"].widget.attrs["placeholder"] = "Password"
        self.fields["password1"].label = ""
        self.fields["password1"].help_text = (
            "<ul class=\"form-text text-muted small\"><li>Your password can't be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can't be a commonly used password.</li><li>Your password can't be entirely numeric.</li></ul>"
        )

        self.fields["password2"].widget.attrs["class"] = "form-control"
        self.fields["password2"].widget.attrs["placeholder"] = "Confirm Password"
        self.fields["password2"].label = ""
        self.fields["password2"].help_text = (
            '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'
        )

    def clean_email(self):
        email = self.cleaned_data["email"]
        if self.instance.pk:  # This means the form is for an existing user
            return email
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists!")
        return email

    def clean_username(self):
        username = self.cleaned_data["username"]
        if self.instance.pk:  # This means the form is for an existing user
            return username
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists!")
        return username

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data["profile_picture"]
        if profile_picture:
            img = Image.open(profile_picture)
            width, height = img.size
            if width != height:
                raise ValidationError(
                    "The image must be square (width and height must be equal)."
                )
        return profile_picture
