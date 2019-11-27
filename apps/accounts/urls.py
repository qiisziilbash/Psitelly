from django.urls import path

from apps.accounts import views

urlpatterns = [
    path('accounts/login/',             views.sign_in,                  name='login'),
    path('accounts/profile/',           views.show_profile,             name='profile'),
    path('accounts/editProfile/',       views.edit_profile,             name='editProfile'),
    path('accounts/notifications/',     views.show_notifications,       name='showNotifications'),
    path('accounts/register/',          views.register,                 name='register'),
    path('accounts/forgot/',            views.forgot,                   name='forgot'),
    path('accounts/verifyAccount/',     views.verify_account,           name='verifyAccount'),

    path('ajax/preRegister/',           views.pre_register,             name='preRegister'),
    path('ajax/postRegister/',          views.post_register,            name='postRegister'),

    path('ajax/sendVerificationCode/',  views.send_verification_code,   name='sendVerificationCode'),
    path('ajax/verifyCode/',            views.verify_code,              name='verifyCode'),
    path('ajax/changePassword/',        views.change_password,          name='changePassword'),

    path('ajax/follow/',                views.follow,                   name='follow'),
    path('ajax/unFollow/',              views.unfollow,                 name='unFollow'),

    path('ajax/clearNotifications/',    views.clear_notifications,      name='clearNotifications'),
    path('ajax/deleteNotification/',    views.delete_notifications,     name='deleteNotification'),
]
