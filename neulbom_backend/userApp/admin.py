from django import forms
from django.contrib import admin
from .models import CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.db.models import F


class UserCreationForm(forms.ModelForm):
    username = forms.CharField(label="아이디", widget=forms.TextInput)
    password1 = forms.CharField(label="비밀번호", widget=forms.PasswordInput)
    password2 = forms.CharField(label="비밀번호 확인", widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = ["username", "email"]

    def clean_password(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = get_user_model()
        fields = ["email", "password", "is_active", "is_staff"]


@admin.action(description="학년 올리기")
def plus_grade(UserAdmin, request, queryset):
    CustomUser.objects.filter(role="s").update(grade=F("grade") + 1)


@admin.register(CustomUser)
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = [
        "username",
        "YearOfAdmission",
        "school",
        "grade",
        "is_staff",
        "card_img",
    ]
    list_filter = ["is_staff"]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["school"]}),
        ("Permissions", {"fields": ["is_staff"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["school"]
    filter_horizontal = []
    actions = [plus_grade]


admin.site.unregister(Group)
