from django.db import models
from accounts.models import User
from marketplace.models import Article


class Conversation(models.Model):
    """
    Conversation entre deux utilisateurs à propos d'un article.
    Le badge des participants s'affiche dans l'en-tête.
    """
    participants  = models.ManyToManyField(User, related_name='conversations')
    article       = models.ForeignKey(Article, on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name='conversations')
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Conversation"
        verbose_name_plural = "Conversations"
        ordering = ['-updated_at']

    def __str__(self):
        noms = ', '.join(u.get_full_name() or u.username for u in self.participants.all())
        return f"Conv: {noms}"

    def autre_participant(self, user):
        """Retourne l'autre participant de la conversation."""
        return self.participants.exclude(pk=user.pk).first()

    def dernier_message(self):
        return self.messages_conv.order_by('-created_at').first()

    def nb_non_lus(self, user):
        return self.messages_conv.filter(is_read=False).exclude(expediteur=user).count()

    @classmethod
    def get_or_create_between(cls, user1, user2, article=None):
        """Trouve ou crée une conversation entre deux utilisateurs."""
        conv = cls.objects.filter(
            participants=user1
        ).filter(
            participants=user2
        ).filter(
            article=article
        ).first()
        if not conv:
            conv = cls.objects.create(article=article)
            conv.participants.add(user1, user2)
        return conv


class Message(models.Model):
    """Message dans une conversation."""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE,
                                      related_name='messages_conv')
    expediteur   = models.ForeignKey(User, on_delete=models.CASCADE,
                                      related_name='messages_envoyes')
    contenu      = models.TextField()
    is_read      = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Message"
        verbose_name_plural = "Messages"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.expediteur} : {self.contenu[:50]}"
