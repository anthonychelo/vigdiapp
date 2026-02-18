from django.contrib import admin
from django.utils.html import format_html
from .models import Article, ArticlePhoto, DemandeEchange, Evaluation, DemandeArticle


class ArticlePhotoInline(admin.TabularInline):
    model  = ArticlePhoto
    extra  = 1
    max_num = 5
    fields  = ('apercu_photo', 'image', 'ordre')
    readonly_fields = ('apercu_photo',)

    def apercu_photo(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:60px;border-radius:4px;" />', obj.image.url)
        return "—"
    apercu_photo.short_description = "Aperçu"


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display   = ('vignette', 'titre', 'vendeur_badge', 'categorie',
                       'type_transaction', 'prix_affiche', 'statut', 'vues', 'created_at')
    list_filter    = ('categorie', 'type_transaction', 'statut', 'condition')
    search_fields  = ('titre', 'vendeur__username', 'vendeur__first_name')
    list_editable  = ('statut',)
    inlines        = [ArticlePhotoInline]
    readonly_fields = ('vues', 'created_at', 'updated_at')
    ordering       = ['-created_at']

    def vignette(self, obj):
     try:   
        photo = obj.photo_principale
        if photo and hasattr(photo, 'url') and photo.url:
            return format_html('<img src="{}" style="height:45px;width:45px;object-fit:cover;border-radius:6px;" />', photo.url)
     except Exception:
        
        return "📦"
    vignette.short_description = ""

    def vendeur_badge(self, obj):
        if obj.vendeur.afficher_badge:
            return format_html('{} <b>{}</b> {}',
                obj.vendeur.badge.icone,
                obj.vendeur.get_full_name() or obj.vendeur.username,
                '')
        return obj.vendeur.get_full_name() or obj.vendeur.username
    vendeur_badge.short_description = "Vendeur"

    def prix_affiche(self, obj):
        if obj.type_transaction == 'don':
            return format_html('<span style="color:#10b981;">Don gratuit</span>')
        return format_html('{} <small>FCFA</small>', f"{obj.prix:,}".replace(',', ' '))
    prix_affiche.short_description = "Prix"


@admin.register(DemandeEchange)
class DemandeEchangeAdmin(admin.ModelAdmin):
    list_display  = ('demandeur', 'article_propose', 'apercu_livre', 'statut', 'created_at')
    list_filter   = ('statut',)
    list_editable = ('statut',)
    readonly_fields = ('apercu_livre_grand', 'demandeur', 'article_propose',
                        'titre_livre', 'description_livre', 'photo_livre',
                        'message', 'created_at')

    def apercu_livre(self, obj):
        if obj.photo_livre:
            return format_html('<img src="{}" style="height:50px;border-radius:4px;" />', obj.photo_livre.url)
        return "—"
    apercu_livre.short_description = "Photo livre proposé"

    def apercu_livre_grand(self, obj):
        if obj.photo_livre:
            return format_html('<img src="{}" style="max-height:200px;border-radius:8px;" />', obj.photo_livre.url)
        return "Pas de photo"
    apercu_livre_grand.short_description = "Photo du livre proposé"


@admin.register(DemandeArticle)
class DemandeArticleAdmin(admin.ModelAdmin):
    list_display   = ('demandeur', 'nom_article', 'categorie', 'budget_max', 'statut', 'created_at')
    list_filter    = ('statut', 'categorie')
    search_fields  = ('nom_article', 'demandeur__username')
    list_editable  = ('statut',)
    readonly_fields = ('demandeur', 'nom_article', 'categorie', 'description',
                        'budget_max', 'created_at')
    actions = ['approuver', 'refuser']

    @admin.action(description="✅ Approuver les demandes sélectionnées")
    def approuver(self, request, queryset):
        queryset.update(statut='approuvee')

    @admin.action(description="❌ Refuser les demandes sélectionnées")
    def refuser(self, request, queryset):
        queryset.update(statut='refusee')


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display  = ('acheteur', 'vendeur', 'note_etoiles', 'article', 'created_at')
    list_filter   = ('note',)
    search_fields = ('acheteur__username', 'vendeur__username')
    readonly_fields = ('acheteur', 'vendeur', 'article', 'note', 'commentaire', 'created_at')

    def note_etoiles(self, obj):
        etoiles = '⭐' * obj.note + '☆' * (5 - obj.note)
        return format_html('<span title="{}/5">{}</span>', obj.note, etoiles)
    note_etoiles.short_description = "Note"
