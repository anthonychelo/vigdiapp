#!/bin/bash
# ============================================================
#  ViGDi — Script d'installation et de démarrage
# ============================================================

set -e   # Arrêter si erreur

echo "======================================"
echo "  📦 Installation de ViGDi"
echo "======================================"

# 1. Créer l'environnement virtuel
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Environnement virtuel créé"
fi

# 2. Activer
source venv/bin/activate

# 3. Installer les dépendances
echo "📥 Installation des dépendances..."
pip install -q django pillow python-decouple whitenoise crispy-bootstrap5 django-crispy-forms

# 4. Copier .env si non existant
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Fichier .env créé (éditer avant la production !)"
fi

# 5. Créer les dossiers media
mkdir -p media/{profiles,articles,echanges,verifications,badges}
echo "✅ Dossiers media créés"

# 6. Migrations
echo "⚙️  Application des migrations..."
python manage.py makemigrations accounts marketplace messaging badges
python manage.py migrate

# 7. Créer le superuser si non existant
echo ""
echo "👤 Créer le compte administrateur :"
python manage.py createsuperuser --noinput \
    --username admin \
    --email admin@videgrenier.cm 2>/dev/null || echo "  (superuser 'admin' existe déjà)"

# 8. Collecter les fichiers statiques
python manage.py collectstatic --noinput -v 0

echo ""
echo "======================================"
echo "  🚀 Démarrage du serveur"
echo "======================================"
echo "  Marché    → http://127.0.0.1:8000/marketplace/"
echo "  Admin     → http://127.0.0.1:8000/admin/"
echo "  Login     → admin / (mot de passe défini manuellement)"
echo ""
echo "  Pour définir le mot de passe admin :"
echo "  python manage.py changepassword admin"
echo "======================================"
echo ""

python manage.py runserver
