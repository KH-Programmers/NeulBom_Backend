from .views import RegisterView, LoginView, Profile, Authentication
from knox import views as knox_views
from django.urls import include, path
from django.contrib.auth import views as auth_views

app_name = "userApp"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/<int:pk>/", Profile.as_view(), name="profile"),
    path("logout/", knox_views.LogoutView.as_view(), name="logout"),
    path(
        "password_reset/",
        include("django_rest_passwordreset.urls", namespace="password_reset"),
    ),
    path("authentication/", Authentication.as_view(), name="authentication"),

	path('password-reset/',	
		auth_views.PasswordResetView.as_view(
		template_name='users/password_reset.html'
		),
		name='password_reset'),

	path('password-reset/done/',	
		auth_views.PasswordResetDoneView.as_view(
			template_name='users/password_reset_done.html'
		),
		name='password_reset_done'),

	path('password-reset-confirm/<uidb64>/<token>/',	
		auth_views.PasswordResetConfirmView.as_view(
			template_name='users/password_reset_confirm.html'
		),
		name='password_reset_confirm'),

	path('password-reset-complete/',	
		auth_views.PasswordResetCompleteView.as_view(
			template_name='users/password_reset_complete.html'
		),
		name='password_reset_complete'),

	
	path("profile/password-change/", auth_views.PasswordChangeView.as_view(
        template_name='users/password_change.html'
    ), name='password_change'),

    path("profile/password-reset/", auth_views.PasswordResetView.as_view(
        template_name='users/password_reset_profile.html',
        email_template_name='users/password_reset_profile_email.html'
    ), name='password_reset_profile'),

    path("profile/certification/", Authentication.as_view(), name='authentication'),
]
