# 🛍️ ViGDiM — Backend Django

Application de marché camerounais développée en **Python + Django pur**.

---

## 🗂️ Structure du projet

```
videgrenier_cm/
├── manage.py
├── requirements.txt
├── .env.example          ← Copier en .env
├── start.sh              ← Script d'installation automatique
│
├── videgrenier_cm/       ← Projet Django (settings, urls, wsgi)
│   ├── settings.py
│   └── urls.py
│
├── accounts/             ← Utilisateurs, badges, certification
│   ├── models.py         → User, Badge, DemandeVerification
│   ├── admin.py          → Interface admin pour badges et users
│   ├── views.py          → Inscription, connexion, profil
│   ├── forms.py
│   └── context_processors.py → Badge injecté dans tous les templates
│
├── marketplace/          ← Articles, échanges, demandes
│   ├── models.py         → Article, ArticlePhoto, DemandeEchange, DemandeArticle
│   ├── admin.py
│   ├── views.py
│   └── forms.py
│
├── messaging/            ← Conversations et messages
│   └── models.py         → Conversation, Message
│
├── templates/            ← Tous les templates HTML Bootstrap 5
│   ├── base.html
│   ├── accounts/
│   ├── marketplace/
│   └── messaging/
│
└── media/                ← Créé automatiquement
    ├── profiles/         → Photos de profil
    ├── articles/         → Photos des articles
    ├── echanges/         → Photos des livres proposés à l'échange
    ├── badges/           → Images des badges
    └── verifications/    → Documents de certification
```

---

## 🚀 Installation rapide

```bash
# 1. Se placer dans le dossier
cd videgrenier_cm

# 2. Lancer le script (crée le venv, installe, migre, démarre)
bash start.sh

# 3. Définir le mot de passe admin (dans un autre terminal)
python manage.py changepassword admin
```

**Ou manuellement :**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## ✨ Fonctionnalités

### 👤 Utilisateurs
- Inscription avec email, téléphone (6XXXXXXXX), ville, région Cameroun
- Photo de profil uploadable
- Note moyenne calculée automatiquement

### 🏅 Badges (style Instagram)
- L'admin crée des badges (✅ Vérifié, 🔵 Fiable, ⭐ Elite, etc.)
- L'admin attribue un badge à un utilisateur depuis `/admin/`
- Le badge s'affiche **partout** : navbar, profil, messages, annonces
- Les utilisateurs peuvent **demander la certification** via leur profil

### 📦 Marché
- Publication d'articles avec **jusqu'à 5 photos**
- Catégories : Livres, Électronique, Vêtements, Sports, Musique, Accessoires, Autres
- Types : Vente, Échange (livres uniquement), Don
- Prix max 5 000 FCFA pour les livres
- Filtres par catégorie, type, région, recherche texte

### 🔄 Échanges de livres
- L'acheteur propose son livre avec une **photo obligatoire**
- Le vendeur accepte ou refuse la proposition
- Suivi des échanges envoyés et reçus

### 💬 Messages
- Conversations liées à un article
- Badge de l'interlocuteur visible dans le chat
- Marquage lu/non-lu automatique

### 📬 Demande d'articles
- Un utilisateur peut demander à l'admin d'ajouter un article
- L'admin voit toutes les demandes dans `/admin/`

---

## 🖼️ Stockage des photos

### Mode LOCAL (développement, défaut)
```env
MEDIA_STORAGE=local
# Les photos → media/ sur votre serveur
```

### Mode AWS S3 (production recommandé)
```env
MEDIA_STORAGE=s3
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_STORAGE_BUCKET_NAME=videgrenier-media
AWS_S3_REGION_NAME=eu-west-1
```
Les photos sont alors stockées dans votre bucket S3, accessibles via URL publique.

---

## 🛡️ Interface Admin

URL : `http://votre-domaine/admin/`

| Section | Actions |
|---------|---------|
| **Badges** | Créer, modifier, activer/désactiver des badges |
| **Utilisateurs** | Certifier, attribuer un badge, voir profils |
| **Demandes de vérification** | Approuver/Refuser en un clic |
| **Articles** | Voir photos inline, changer le statut |
| **Échanges** | Voir la photo du livre proposé |
| **Demandes d'articles** | Approuver/Refuser les demandes |

---

## 🌐 URLs de l'application

| URL | Description |
|-----|-------------|
| `/marketplace/` | Liste des articles |
| `/marketplace/article/<id>/` | Détail d'un article |
| `/marketplace/article/ajouter/` | Publier un article |
| `/marketplace/mes-echanges/` | Gérer ses échanges |
| `/marketplace/demander-article/` | Demande à l'admin |
| `/messages/` | Liste des conversations |
| `/messages/<id>/` | Conversation |
| `/auth/login/` | Connexion |
| `/auth/inscription/` | Inscription |
| `/auth/profil/` | Mon profil |
| `/auth/certification/` | Demander la certification |
| `/admin/` | Interface admin |
