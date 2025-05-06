from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User


class UserCreationForm(DjangoUserCreationForm):
    """This form is used to create new users"""

    class Meta:
        model = User
        fields = [
            "email",
            "id_no",
            "first_name",
            "middle_name",
            "last_name",
            "security_question",
            "security_answer",
            "is_staff",
            "is_superuser",
        ]

    def clean_email(self):
        """Validate the email is unique among all users"""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("A user with this email already exists."))
        return email

    def clean_id_number(self):
        """Check for uniqueness of id number"""
        id_no = self.cleaned_data.get("id_no")
        if User.objects.filter(id_no=id_no).exists():
            raise ValidationError(_("A user with this ID number already exists."))
        return id_no

    def clean(self):
        """Perform additional clean validation"""
        cleaned_data = super().clean()
        is_superuser = cleaned_data.get("is_superuser")
        security_question = cleaned_data.get("security_question")
        security_answer = cleaned_data.get("security_answer")

        """check if user is not a superuser"""
        if not is_superuser:
            if not security_question:
                self.add_error(
                    "security_question",
                    _("Security question is required for regular users"),
                )
            if not security_answer:
                self.add_error(
                    "security_answer",
                    _("Security question is required for regular users"),
                )
        return cleaned_data

    def save(self, commit=True):
        """Override the default save method"""
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class UserChangeForm(DjangoUserChangeForm):
    """This form is used to update existing users."""

    class Meta:
        model = User
        fields = [
            "email",
            "id_no",
            "first_name",
            "middle_name",
            "last_name",
            "security_question",
            "security_answer",
            "is_active",
            "is_staff",
            "is_superuser",
        ]

    def clean_email(self):
        """Validate the email is unique for existing user."""
        email = self.cleaned_data.get("email")
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError(_("A user with this email already exists."))
        return email

    def clean_id_no(self):
        """Validate the ID number is unique for existing user."""
        id_no = self.cleaned_data.get("id_no")
        if User.objects.exclude(pk=self.instance.pk).filter(id_no=id_no).exists():
            raise ValidationError(_("A user with this ID number already exists."))
        return id_no

    def clean(self):
        """Perform additional clean validation"""
        cleaned_data = super().clean()
        is_superuser = cleaned_data.get("is_superuser")
        security_question = cleaned_data.get("security_question")
        security_answer = cleaned_data.get("security_answer")

        """check if user is not a superuser"""
        if not is_superuser:
            if not security_question:
                self.add_error(
                    "security_question",
                    _("Security question is required for regular users"),
                )
            if not security_answer:
                self.add_error(
                    "security_answer",
                    _("Security question is required for regular users"),
                )
        return cleaned_data
