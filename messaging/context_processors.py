# À ajouter dans messaging/context_processors.py

from messaging.models import Message

def unread_messages_count(request):
    """Compte les messages non lus pour l'utilisateur connecté."""
    if request.user.is_authenticated:
        # Compter les messages reçus non lus
        count = Message.objects.filter(
            destinataire=request.user,
            lu=False
        ).count()
        return {'unread_messages_count': count}
    return {'unread_messages_count': 0}