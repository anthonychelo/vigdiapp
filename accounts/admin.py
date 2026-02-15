from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
from .models import User, Badge, DemandeVerification


# ─── Badge ────────────────────────────────────────────────────────────────────
@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display  = ('apercu', 'nom', 'couleur', 'actif', 'nb_utilisateurs')
    list_filter   = ('couleur', 'actif')
    search_fields = ('nom',)
    list_editable = ('actif',)

    def apercu(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:30px;" />', obj.image.url)
        return format_html('<span style="font-size:24px;">{}</span>', obj.icone)
    apercu.short_description = ""

    def nb_utilisateurs(self, obj):
        count = obj.utilisateurs.count()
        return format_html('<b>{}</b>', count)
    nb_utilisateurs.short_description = "Nb porteurs"


# ─── User ─────────────────────────────────────────────────────────────────────
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ('avatar_miniature', 'username', 'get_full_name',
                     'email', 'telephone', 'ville', 'region',
                     'badge_affiche', 'est_certifie', 'note_moyenne', 'is_active')
    list_filter   = ('est_certifie', 'badge', 'region', 'is_active', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'telephone')
    list_editable = ('est_certifie',)
    ordering      = ('-date_joined',)
    actions       = ['certifier_utilisateurs', 'retirer_certification']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profil ViGDi', {
            'fields': ('photo_profil', 'telephone', 'ville', 'region', 'bio'),
        }),
        ('Certification & Badge', {
            'fields': ('est_certifie', 'badge', 'date_certification'),
            'description': (
                "Attribuer un badge certifie l'utilisateur. "
                "Le badge apparaîtra à côté de son nom partout dans l'app."
            ),
        }),
        ('Statistiques', {
            'fields': ('note_moyenne', 'nb_ventes', 'nb_echanges'),
            'classes': ('collapse',),
        }),
    )

    def avatar_miniature(self, obj):
        if obj.photo_profil:
            return format_html(
                '<img src="{}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;" />',
                obj.photo_profil.url
            )
        initiale = (obj.first_name or obj.username)[0].upper()
        return format_html(
            '<div style="width:40px;height:40px;border-radius:50%;background:#4f46e5;'
            'color:white;display:flex;align-items:center;justify-content:center;'
            'font-weight:bold;font-size:16px;">{}</div>',
            initiale
        )
    avatar_miniature.short_description = ""

    def badge_affiche(self, obj):
        if obj.badge and obj.est_certifie:
            couleur_map = {
                'blue': '#3b82f6', 'gold': '#f59e0b',
                'green': '#10b981', 'purple': '#8b5cf6'
            }
            couleur = couleur_map.get(obj.badge.couleur, '#e53e3e')
            return format_html(
                '<span style="color:{};font-weight:bold;">{} {}</span>',
                couleur, obj.badge.icone, obj.badge.nom
            )
        return format_html('<span style="color:#9ca3af;">{}</span>', '—')
    badge_affiche.short_description = "Badge"

    @admin.action(description="✅ Certifier les utilisateurs sélectionnés")
    def certifier_utilisateurs(self, request, queryset):
        updated = queryset.update(est_certifie=True, date_certification=timezone.now())
        self.message_user(request, f"{updated} utilisateur(s) certifié(s).")

    @admin.action(description="❌ Retirer la certification")
    def retirer_certification(self, request, queryset):
        updated = queryset.update(est_certifie=False, date_certification=None)
        self.message_user(request, f"Certification retirée pour {updated} utilisateur(s).")


# ─── Demande de vérification ──────────────────────────────────────────────────
@admin.register(DemandeVerification)
class DemandeVerificationAdmin(admin.ModelAdmin):
    list_display  = ('utilisateur', 'statut', 'created_at', 'actions_rapides')
    list_filter   = ('statut',)
    search_fields = ('utilisateur__username', 'utilisateur__email')
    readonly_fields = ('utilisateur', 'message', 'document', 'created_at')
    actions        = ['approuver_demandes', 'refuser_demandes']
    ordering       = ['-created_at']

    fieldsets = (
        ('Demande', {
            'fields': ('utilisateur', 'message', 'document', 'created_at'),
        }),
        ('Réponse admin', {
            'fields': ('statut', 'reponse_admin'),
        }),
    )

    def actions_rapides(self, obj):
        if obj.statut == 'en_attente':
            url = f'/admin/accounts/demandeverification/{obj.pk}/change/'
            return format_html('<a href="{}" style="color:red;">Voir demande</a>', url)
        return obj.get_statut_display()
    actions_rapides.short_description = "Action"

    @admin.action(description="✅ Approuver et certifier les utilisateurs")
    def approuver_demandes(self, request, queryset):
        for demande in queryset:
            demande.statut = 'approuvee'
            demande.save()
            demande.utilisateur.est_certifie = True
            demande.utilisateur.date_certification = timezone.now()
            demande.utilisateur.save(update_fields=['est_certifie', 'date_certification'])
        self.message_user(request, f"{queryset.count()} demande(s) approuvée(s).")

    @admin.action(description="❌ Refuser les demandes")
    def refuser_demandes(self, request, queryset):
        queryset.update(statut='refusee')
        self.message_user(request, f"{queryset.count()} demande(s) refusée(s).")