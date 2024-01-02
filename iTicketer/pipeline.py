from social.apps.django_app.default.models import UserSocialAuth
from django.contrib.auth.models import User

def social_user(backend, uid, user=None, *args, **kwargs):
    provider = backend.name
    # social = backend.strategy.storage.user.get_social_auth(provider, uid)
    
    if UserSocialAuth.objects.filter(provider=provider, uid=uid).exists():
        social = UserSocialAuth.objects.filter(provider=provider, uid=uid).first()
    else:
        social = None

    if not social:
        user = User.objects.filter(email=uid)
        if user.exists():
            social = UserSocialAuth.objects.create(provider=provider,uid=uid,user=user.first())


    if social:
        if user and social.user != user:
            return backend.strategy.redirect("/error")

        elif not user:
            user = social.user
    else:
        user = None
    return {
        "social": social,
        "user": user,
        "is_new": user is None,
        "new_association": social is None,
    }
