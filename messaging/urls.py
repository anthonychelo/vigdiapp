from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('',                                         views.liste_conversations,  name='liste'),
    path('<int:conv_pk>/',                           views.conversation,         name='conversation'),
    path('demarrer/<int:user_pk>/',                  views.demarrer_conversation, name='demarrer'),
    path('demarrer/<int:user_pk>/article/<int:article_pk>/',
                                                     views.demarrer_conversation, name='demarrer_article'),
]
