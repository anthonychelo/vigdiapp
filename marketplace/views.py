from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Article, ArticlePhoto, DemandeEchange, DemandeArticle, Evaluation
from .forms import (ArticleForm, PhotoFormSet, DemandeEchangeForm,
                    DemandeArticleForm, EvaluationForm)


def liste_articles(request):
    """Page principale du marché avec filtres et recherche."""
    articles = Article.objects.filter(statut='disponible').select_related('vendeur', 'vendeur__badge')

    # Filtres
    q         = request.GET.get('q', '').strip()
    categorie = request.GET.get('categorie', '')
    type_tr   = request.GET.get('type', '')
    region    = request.GET.get('region', '')

    if q:
        articles = articles.filter(
            Q(titre__icontains=q) | Q(description__icontains=q) | Q(ville__icontains=q)
        )
    if categorie:
        articles = articles.filter(categorie=categorie)
    if type_tr:
        articles = articles.filter(type_transaction=type_tr)
    if region:
        articles = articles.filter(region=region)

    # Précharger les photos
    articles = articles.prefetch_related('photos')

    paginator = Paginator(articles, 12)
    page      = paginator.get_page(request.GET.get('page'))

    from accounts.models import User
    context = {
        'articles':         page,
        'categories':       Article.CATEGORIE_CHOICES,
        'types':            Article.TYPE_CHOICES,
        'regions':          User.REGION_CHOICES,
        'q':                q,
        'categorie_active': categorie,
        'type_actif':       type_tr,
    }
    return render(request, 'marketplace/liste.html', context)


def detail_article(request, pk):
    """Détail d'un article avec demande d'échange si applicable."""
    article = get_object_or_404(
        Article.objects.select_related('vendeur', 'vendeur__badge').prefetch_related('photos'),
        pk=pk
    )
    # Incrémenter les vues
    Article.objects.filter(pk=pk).update(vues=article.vues + 1)

    # Demandes d'échange existantes pour cet article
    ma_demande = None
    form_echange = None
    if request.user.is_authenticated and article.est_echangeable:
        ma_demande = DemandeEchange.objects.filter(
            article_propose=article,
            demandeur=request.user
        ).first()
        if not ma_demande:
            form_echange = DemandeEchangeForm()

    # Évaluations du vendeur
    evaluations = Evaluation.objects.filter(vendeur=article.vendeur).order_by('-created_at')[:5]

    context = {
        'article':      article,
        'form_echange': form_echange,
        'ma_demande':   ma_demande,
        'evaluations':  evaluations,
    }
    return render(request, 'marketplace/detail.html', context)


@login_required
def ajouter_article(request):
    """Publier un nouvel article avec jusqu'à 5 photos."""
    if request.method == 'POST':
        form     = ArticleForm(request.POST)
        formset  = PhotoFormSet(request.POST, request.FILES, prefix='photos')

        if form.is_valid() and formset.is_valid():
            article          = form.save(commit=False)
            article.vendeur  = request.user
            article.ville    = article.ville or request.user.ville
            article.region   = article.region or request.user.region
            article.save()

            # Sauvegarder les photos
            photos = formset.save(commit=False)
            for i, photo in enumerate(photos):
                photo.article = article
                photo.ordre   = i
                photo.save()

            messages.success(request, "Votre article a été publié avec succès !")
            return redirect('marketplace:detail', pk=article.pk)
    else:
        form    = ArticleForm()
        formset = PhotoFormSet(prefix='photos')

    return render(request, 'marketplace/ajouter.html', {
        'form': form, 'formset': formset
    })


@login_required
def modifier_article(request, pk):
    """Modifier son article."""
    article = get_object_or_404(Article, pk=pk, vendeur=request.user)

    if request.method == 'POST':
        form    = ArticleForm(request.POST, instance=article)
        formset = PhotoFormSet(request.POST, request.FILES,
                                instance=article, prefix='photos')
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Article modifié !")
            return redirect('marketplace:detail', pk=article.pk)
    else:
        form    = ArticleForm(instance=article)
        formset = PhotoFormSet(instance=article, prefix='photos')

    return render(request, 'marketplace/modifier.html', {
        'form': form, 'formset': formset, 'article': article
    })


@login_required
def supprimer_article(request, pk):
    article = get_object_or_404(Article, pk=pk, vendeur=request.user)
    if request.method == 'POST':
        article.statut = 'retire'
        article.save()
        messages.success(request, "Article retiré du marché.")
        return redirect('accounts:profil')
    return render(request, 'marketplace/confirmer_suppression.html', {'article': article})


@login_required
def demande_echange(request, article_pk):
    """Soumettre une demande d'échange avec photo du livre proposé."""
    article = get_object_or_404(Article, pk=article_pk, type_transaction='echanger',
                                 statut='disponible')

    if article.vendeur == request.user:
        messages.error(request, "Vous ne pouvez pas échanger votre propre article.")
        return redirect('marketplace:detail', pk=article_pk)

    # Vérifier demande existante
    if DemandeEchange.objects.filter(article_propose=article,
                                      demandeur=request.user,
                                      statut='en_attente').exists():
        messages.info(request, "Vous avez déjà une demande en attente pour cet article.")
        return redirect('marketplace:detail', pk=article_pk)

    if request.method == 'POST':
        form = DemandeEchangeForm(request.POST, request.FILES)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.article_propose = article
            demande.demandeur       = request.user
            demande.save()
            messages.success(request,
                "Votre proposition d'échange a été envoyée au vendeur !")
            return redirect('marketplace:detail', pk=article_pk)
    else:
        form = DemandeEchangeForm()

    return render(request, 'marketplace/demande_echange.html', {
        'form': form, 'article': article
    })


@login_required
def mes_demandes_echange(request):
    """Voir les demandes d'échange reçues (côté vendeur) et envoyées."""
    demandes_recues  = DemandeEchange.objects.filter(
        article_propose__vendeur=request.user
    ).select_related('demandeur', 'demandeur__badge', 'article_propose')

    demandes_envoyees = DemandeEchange.objects.filter(
        demandeur=request.user
    ).select_related('article_propose', 'article_propose__vendeur')

    return render(request, 'marketplace/mes_demandes.html', {
        'demandes_recues':  demandes_recues,
        'demandes_envoyees': demandes_envoyees,
    })


@login_required
def repondre_echange(request, demande_pk, action):
    """Vendeur accepte ou refuse une demande d'échange."""
    demande = get_object_or_404(
        DemandeEchange,
        pk=demande_pk,
        article_propose__vendeur=request.user,
        statut='en_attente'
    )
    if action == 'accepter':
        demande.statut = 'acceptee'
        demande.article_propose.statut = 'vendu'
        demande.article_propose.save()
        # Incrémenter les échanges
        request.user.nb_echanges += 1
        request.user.save(update_fields=['nb_echanges'])
        messages.success(request, "Échange accepté ! Contactez le demandeur.")
    elif action == 'refuser':
        demande.statut = 'refusee'
        messages.info(request, "Demande refusée.")
    demande.save()
    return redirect('marketplace:mes_demandes')


@login_required
def demande_article(request):
    """L'utilisateur demande à l'admin d'ajouter un article."""
    if request.method == 'POST':
        form = DemandeArticleForm(request.POST)
        if form.is_valid():
            demande             = form.save(commit=False)
            demande.demandeur   = request.user
            demande.save()
            messages.success(request,
                "Votre demande a été envoyée à l'admin. "
                "Il sera notifié prochainement."
            )
            return redirect('marketplace:liste')
    else:
        form = DemandeArticleForm()

    mes_demandes = DemandeArticle.objects.filter(
        demandeur=request.user
    ).order_by('-created_at')

    return render(request, 'marketplace/demande_article.html', {
        'form': form,
        'mes_demandes': mes_demandes,
    })
