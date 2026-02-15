from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('inscription/',          views.InscriptionView.as_view(), name='inscription'),
    path('login/',                views.ConnexionView.as_view(),   name='connexion'),
    path('logout/',               views.deconnexion,               name='deconnexion'),
    path('profil/',               views.profil,                    name='profil'),
    path('profil/<int:pk>/',      views.profil,                    name='profil_utilisateur'),
    path('profil/modifier/',      views.modifier_profil,           name='modifier_profil'),
    path('certification/',        views.demande_verification,      name='demande_verification'),
]
