from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import View
from .forms import InscriptionForm, ConnexionForm, ProfilForm, DemandeVerificationForm
from .models import User, DemandeVerification


class InscriptionView(View):
    template_name = 'accounts/inscription.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('marketplace:liste')
        return render(request, self.template_name, {'form': InscriptionForm()})

    def post(self, request):
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.first_name} ! Votre compte a été créé.")
            return redirect('marketplace:liste')
        return render(request, self.template_name, {'form': form})


class ConnexionView(View):
    template_name = 'accounts/connexion.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('marketplace:liste')
        return render(request, self.template_name, {'form': ConnexionForm()})

    def post(self, request):
        form = ConnexionForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenue {user.first_name or user.username} !")
            return redirect(request.GET.get('next', 'marketplace:liste'))
        return render(request, self.template_name, {'form': form})


@login_required
def deconnexion(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('accounts:connexion')


@login_required
def profil(request, pk=None):
    """Profil d'un utilisateur – si pk=None, affiche le profil courant."""
    if pk:
        utilisateur = get_object_or_404(User, pk=pk)
        est_mon_profil = (utilisateur == request.user)
    else:
        utilisateur = request.user
        est_mon_profil = True

    from marketplace.models import Article
    articles = Article.objects.filter(vendeur=utilisateur, statut='disponible').order_by('-created_at')

    context = {
        'utilisateur':   utilisateur,
        'est_mon_profil': est_mon_profil,
        'articles':      articles,
    }
    return render(request, 'accounts/profil.html', context)


@login_required
def modifier_profil(request):
    """Modifier son profil et sa photo de profil."""
    if request.method == 'POST':
        form = ProfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès !")
            return redirect('accounts:profil')
    else:
        form = ProfilForm(instance=request.user)
    return render(request, 'accounts/modifier_profil.html', {'form': form})


@login_required
def demande_verification(request):
    """L'utilisateur envoie une demande de certification à l'admin."""
    # Vérifier s'il y a déjà une demande en attente
    demande_en_cours = DemandeVerification.objects.filter(
        utilisateur=request.user, statut='en_attente'
    ).first()

    if request.method == 'POST' and not demande_en_cours:
        form = DemandeVerificationForm(request.POST, request.FILES)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.utilisateur = request.user
            demande.save()
            messages.success(request,
                "Votre demande de certification a été envoyée ! "
                "L'admin vous répondra prochainement."
            )
            return redirect('accounts:profil')
    else:
        form = DemandeVerificationForm()

    mes_demandes = DemandeVerification.objects.filter(
        utilisateur=request.user
    ).order_by('-created_at')

    return render(request, 'accounts/demande_verification.html', {
        'form': form,
        'demande_en_cours': demande_en_cours,
        'mes_demandes': mes_demandes,
    })
