from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('',                                  views.liste_articles,    name='liste'),
    path('article/<int:pk>/',                 views.detail_article,    name='detail'),
    path('article/ajouter/',                  views.ajouter_article,   name='ajouter'),
    path('article/<int:pk>/modifier/',        views.modifier_article,  name='modifier'),
    path('article/<int:pk>/supprimer/',       views.supprimer_article, name='supprimer'),
    # Échanges
    path('article/<int:article_pk>/echanger/',views.demande_echange,   name='demande_echange'),
    path('mes-echanges/',                      views.mes_demandes_echange, name='mes_demandes'),
    path('echange/<int:demande_pk>/<str:action>/', views.repondre_echange, name='repondre_echange'),
    # Demande d'article à l'admin
    path('demander-article/',                 views.demande_article,   name='demande_article'),
     path('ai-pricing/', views.ai_pricing_suggestion, name='ai_pricing'),
    path('confirmer/', views.confirmer_article, name='confirmer_article'),
]
