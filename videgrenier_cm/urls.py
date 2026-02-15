from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Personnalisation de l'interface admin
admin.site.site_header  = "ViGDi – Administration"
admin.site.site_title   = "ViGDi"
admin.site.index_title  = "Tableau de bord"

urlpatterns = [
    path('admin/',       admin.site.urls),
    path('auth/',        include('accounts.urls',     namespace='accounts')),
    path('marketplace/', include('marketplace.urls',  namespace='marketplace')),
    path('messages/',    include('messaging.urls',    namespace='messaging')),
    path('badges/',      include('badges.urls',       namespace='badges')),
    path('',             include('marketplace.urls',  namespace='home')),   # redirection racine
]

# Servir les médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
