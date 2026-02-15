import os
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User


def article_photo_path(instance, filename):
    """Stocke les photos dans media/articles/<article_id>/"""
    ext = os.path.splitext(filename)[1]
    import uuid
    return f'articles/{instance.article.id}/{uuid.uuid4().hex}{ext}'


def echange_photo_path(instance, filename):
    """Photo du livre proposé en échange."""
    ext = os.path.splitext(filename)[1]
    import uuid
    return f'echanges/{instance.id}/{uuid.uuid4().hex}{ext}'


class Article(models.Model):
    """
    Annonce publiée sur le marché.
    Règles métier :
    - Type "échange" → seulement pour les Livres
    - Prix des livres ≤ 5 000 FCFA
    - Jusqu'à 5 photos par article
    """
    CATEGORIE_CHOICES = [
        ('Livres',       'Livres'),
        ('Electronique', 'Électronique'),
        ('Vetements',    'Vêtements'),
        ('Sports',       'Sports'),
        ('Musique',      'Musique'),
        ('Accessoires',  'Accessoires'),
        ('Autres',       'Autres'),
    ]
    CONDITION_CHOICES = [
        ('neuf',        'Neuf'),
        ('tres_bon',    'Très bon état'),
        ('bon',         'Bon état'),
        ('moyen',       'État moyen'),
        ('reparer',     'À réparer'),
    ]
    TYPE_CHOICES = [
        ('vendre',   'À vendre'),
        ('echanger', 'À échanger'),
        ('don',      'Don'),
    ]
    STATUT_CHOICES = [
        ('disponible', 'Disponible'),
        ('reserve',    'Réservé'),
        ('vendu',      'Vendu / Échangé'),
        ('retire',     'Retiré'),
    ]

    vendeur     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    titre       = models.CharField(max_length=150)
    description = models.TextField()
    prix        = models.PositiveIntegerField(help_text="Prix en FCFA (0 pour les dons)")
    categorie   = models.CharField(max_length=20, choices=CATEGORIE_CHOICES)
    condition   = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='bon')
    type_transaction = models.CharField(max_length=10, choices=TYPE_CHOICES, default='vendre')
    statut      = models.CharField(max_length=12, choices=STATUT_CHOICES, default='disponible')
    ville       = models.CharField(max_length=100, blank=True)
    region      = models.CharField(max_length=20, blank=True)
    vues        = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Article"
        verbose_name_plural = "Articles"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['categorie', 'statut']),
            models.Index(fields=['vendeur', 'statut']),
            models.Index(fields=['type_transaction']),
        ]

    def __str__(self):
        return f"{self.titre} — {self.vendeur}"

    def save(self, *args, **kwargs):
        # Règle : l'échange est seulement pour les livres
        if self.type_transaction == 'echanger' and self.categorie != 'Livres':
            raise ValueError("L'échange est réservé aux livres.")
        # Règle : prix max 5000 FCFA pour les livres
        if self.categorie == 'Livres' and self.prix > 5000:
            raise ValueError("Le prix d'un livre ne peut pas dépasser 5 000 FCFA.")
        super().save(*args, **kwargs)

    @property
    def photo_principale(self):
        """Retourne la première photo ou None."""
        photo = self.photos.first()
        return photo.image if photo else None

    @property
    def est_echangeable(self):
        return self.type_transaction == 'echanger' and self.statut == 'disponible'


class ArticlePhoto(models.Model):
    """Photos associées à un article (max 5)."""
    article    = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='photos')
    image      = models.ImageField(upload_to=article_photo_path)
    ordre      = models.PositiveSmallIntegerField(default=0, help_text="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Photo d'article"
        verbose_name_plural = "Photos d'articles"
        ordering = ['ordre', 'created_at']

    def __str__(self):
        return f"Photo {self.ordre} de « {self.article.titre} »"


class DemandeEchange(models.Model):
    """
    Quand un utilisateur veut échanger un livre,
    il propose son propre livre avec une photo.
    """
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('acceptee',   'Acceptée'),
        ('refusee',    'Refusée'),
        ('annulee',    'Annulée'),
    ]

    article_propose   = models.ForeignKey(Article, on_delete=models.CASCADE,
                                          related_name='demandes_recues',
                                          help_text="Le livre mis en échange par le vendeur")
    demandeur         = models.ForeignKey(User, on_delete=models.CASCADE,
                                          related_name='demandes_echange_envoyees')
    # Le livre proposé par le demandeur
    titre_livre       = models.CharField(max_length=150,
                                          help_text="Titre du livre que vous proposez")
    description_livre = models.TextField(blank=True,
                                          help_text="Description de votre livre")
    photo_livre       = models.ImageField(upload_to=echange_photo_path,
                                          help_text="Photo de votre livre (obligatoire)")
    message           = models.TextField(blank=True,
                                          help_text="Message au vendeur")
    statut            = models.CharField(max_length=12, choices=STATUT_CHOICES,
                                          default='en_attente')
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Demande d'échange"
        verbose_name_plural = "Demandes d'échange"
        ordering = ['-created_at']
        # Un demandeur ne peut faire qu'une seule demande active par article
        constraints = [
            models.UniqueConstraint(
                fields=['article_propose', 'demandeur'],
                condition=models.Q(statut='en_attente'),
                name='unique_demande_active'
            )
        ]

    def __str__(self):
        return f"{self.demandeur} → {self.article_propose.titre}"


class Evaluation(models.Model):
    """Note laissée à un vendeur après une transaction."""
    vendeur     = models.ForeignKey(User, on_delete=models.CASCADE,
                                    related_name='evaluations_recues')
    acheteur    = models.ForeignKey(User, on_delete=models.CASCADE,
                                    related_name='evaluations_donnees')
    article     = models.ForeignKey(Article, on_delete=models.SET_NULL,
                                    null=True, blank=True)
    note        = models.PositiveSmallIntegerField(
                    validators=[MinValueValidator(1), MaxValueValidator(5)])
    commentaire = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Évaluation"
        verbose_name_plural = "Évaluations"
        ordering = ['-created_at']
        unique_together = ('vendeur', 'acheteur', 'article')

    def __str__(self):
        return f"{self.acheteur} → {self.vendeur} : {self.note}/5"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.vendeur.recalcul_note()


class DemandeArticle(models.Model):
    """
    Un utilisateur demande à l'admin d'ajouter un article spécifique
    (ex: un livre introuvable sur la plateforme).
    """
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuvee',  'Approuvée'),
        ('refusee',    'Refusée'),
    ]

    demandeur   = models.ForeignKey(User, on_delete=models.CASCADE,
                                    related_name='demandes_articles')
    nom_article = models.CharField(max_length=200, help_text="Nom de l'article souhaité")
    categorie   = models.CharField(max_length=20, choices=Article.CATEGORIE_CHOICES)
    description = models.TextField(help_text="Décrivez l'article que vous recherchez")
    budget_max  = models.PositiveIntegerField(default=0, help_text="Budget max en FCFA (0 = flexible)")
    statut      = models.CharField(max_length=12, choices=STATUT_CHOICES, default='en_attente')
    reponse_admin = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Demande d'article"
        verbose_name_plural = "Demandes d'articles"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.demandeur} demande : {self.nom_article}"
