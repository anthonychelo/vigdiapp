import os
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


def profil_photo_path(instance, filename):
    """Stocke la photo de profil dans media/profiles/<user_id>/"""
    ext = os.path.splitext(filename)[1]
    return f'profiles/{instance.id}/avatar{ext}'


class Badge(models.Model):
    """
    Badge créé par l'admin (style Instagram).
    Ex : ✅ Vendeur certifié | 🔵 Acheteur fiable | ⭐ Top Échangeur
    """
    BADGE_COULEUR_CHOICES = [
        ('blue',   '🔵 Bleu (vérifié)'),
        ('gold',   '🟡 Or (premium)'),
        ('green',  '🟢 Vert (fiable)'),
        ('purple', '🟣 Violet (élite)'),
    ]
    nom          = models.CharField(max_length=80)
    description  = models.TextField(blank=True)
    icone        = models.CharField(max_length=10, default='✅',
                                    help_text="Emoji ou texte court affiché à côté du nom")
    couleur      = models.CharField(max_length=10, choices=BADGE_COULEUR_CHOICES, default='blue')
    image        = models.ImageField(upload_to='badges/', blank=True, null=True,
                                     help_text="Image optionnelle (PNG transparent recommandé)")
    actif        = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Badge"
        verbose_name_plural = "Badges"
        ordering = ['nom']

    def __str__(self):
        return f"{self.icone} {self.nom}"


class User(AbstractUser):
    """
    Utilisateur étendu :
    - Photo de profil
    - Infos Cameroun (ville, région, téléphone)
    - Badge de certification (attribué par l'admin)
    - Statut certifié
    - Note moyenne
    """
    REGION_CHOICES = [
        ('Adamaoua',     'Adamaoua'),
        ('Centre',       'Centre'),
        ('Est',          'Est'),
        ('Extreme-Nord', 'Extrême-Nord'),
        ('Littoral',     'Littoral'),
        ('Nord',         'Nord'),
        ('Nord-Ouest',   'Nord-Ouest'),
        ('Ouest',        'Ouest'),
        ('Sud',          'Sud'),
        ('Sud-Ouest',    'Sud-Ouest'),
    ]

    # Champs personnalisés
    telephone    = models.CharField(max_length=20, blank=True,
                                    help_text="Format : 6XXXXXXXX")
    ville        = models.CharField(max_length=100, blank=True)
    region       = models.CharField(max_length=20, choices=REGION_CHOICES, blank=True)
    photo_profil = models.ImageField(upload_to=profil_photo_path, blank=True, null=True,
                                     help_text="Photo de profil de l'utilisateur")
    bio          = models.TextField(max_length=300, blank=True)

    # Certification & badge
    est_certifie = models.BooleanField(default=False,
                                       help_text="Coché par l'admin après vérification")
    badge        = models.ForeignKey(Badge, null=True, blank=True,
                                     on_delete=models.SET_NULL,
                                     related_name='utilisateurs',
                                     help_text="Badge attribué à cet utilisateur")
    date_certification = models.DateTimeField(null=True, blank=True)

    # Statistiques
    note_moyenne = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    nb_ventes    = models.PositiveIntegerField(default=0)
    nb_echanges  = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name        = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name() or self.username}"

    @property
    def afficher_badge(self):
        """Retourne True si l'utilisateur a un badge actif et est certifié."""
        return self.est_certifie and self.badge and self.badge.actif

    @property
    def badge_html(self):
        """Renvoie l'icône du badge ou une chaîne vide."""
        if self.afficher_badge:
            return self.badge.icone
        return ''

    def recalcul_note(self):
        """Recalcule la note moyenne à partir des évaluations reçues."""
        from marketplace.models import Evaluation
        evals = Evaluation.objects.filter(vendeur=self)
        if evals.exists():
            total = sum(e.note for e in evals)
            self.note_moyenne = round(total / evals.count(), 1)
            self.save(update_fields=['note_moyenne'])


class DemandeVerification(models.Model):
    """
    Un utilisateur envoie une demande de vérification à l'admin.
    L'admin peut ensuite attribuer un badge depuis l'interface admin.
    """
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuvee',  'Approuvée'),
        ('refusee',    'Refusée'),
    ]

    utilisateur  = models.ForeignKey(User, on_delete=models.CASCADE,
                                     related_name='demandes_verification')
    message      = models.TextField(help_text="Pourquoi souhaitez-vous être certifié ?")
    document     = models.FileField(upload_to='verifications/', blank=True, null=True,
                                    help_text="Document justificatif (CNI, etc.)")
    statut       = models.CharField(max_length=15, choices=STATUT_CHOICES, default='en_attente')
    reponse_admin = models.TextField(blank=True, help_text="Réponse/Note de l'admin")
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Demande de verification"
        verbose_name_plural = "Demandes de verification"
        ordering = ['-created_at']
        db_table = 'accounts_demandeverification'

    def __str__(self):
        return f"Demande de {self.utilisateur} – {self.get_statut_display()}"