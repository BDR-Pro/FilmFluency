
def is_user_active(user):
    try:
        profile = UserSettings.objects.get(user=user)
        return profile.is_active
    except:
        return False