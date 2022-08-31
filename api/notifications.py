import api.models

def created_guest_notification(instance):
    api.models.update_game_session_full_field(instance.game_session.pk)
    clean_date = (instance.game_session.datetime).strftime("%a, %b, %d")
    clean_time = (instance.game_session.datetime).strftime("%I:%M %p")
    if instance.user != instance.game_session.host:
            api.models.NotificationGameSession.objects.create(
                sender=instance.user,
                reciever=instance.game_session.host,
                message=(f"Good news, {instance.user.first_name} would like to join your game on {clean_date} at {clean_time}. Please go to My Games to respond."),
                game_session = instance.game_session,
            )

def updated_guest_notification(instance):
    clean_date = (instance.game_session.datetime).strftime("%a, %b, %d")
    clean_time = (instance.game_session.datetime).strftime("%I:%M %p")
    api.models.update_game_session_confirmed_field(instance.game_session.pk)
    api.models.update_game_session_full_field(instance.game_session.pk)
    if instance.status == "Accepted":
        response = f"Yay! {instance.game_session.host.first_name} has confirmed your game on {clean_date} at {clean_time}. You can see all of your confirmed games on the My Games page."
    elif instance.status == "Rejected":
        response = f"Darn, {instance.game_session.host.first_name} isn't available to play on {clean_date} anymore, but you can sign up for a different game on the Open Games page."
    else:
        response = f"Your guest request status has changed to {instance.status}"

    api.models.NotificationGameSession.objects.create(
            sender=instance.game_session.host,
            reciever=instance.user,
            message=response,
            game_session = instance.game_session,
        )