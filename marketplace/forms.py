from django import forms
from .models import Article, ArticlePhoto, DemandeEchange, DemandeArticle, Evaluation


class ArticleForm(forms.ModelForm):
    class Meta:
        model  = Article
        fields = ('titre', 'description', 'prix', 'categorie',
                  'condition', 'type_transaction', 'ville', 'region')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'titre': forms.TextInput(attrs={'placeholder': 'Ex: iPhone 13 Pro 128Go'}),
            'prix':  forms.NumberInput(attrs={'min': 0, 'placeholder': 'Prix en FCFA'}),
        }

    def clean(self):
        cleaned = super().clean()
        cat  = cleaned.get('categorie')
        type_ = cleaned.get('type_transaction')
        prix = cleaned.get('prix', 0)

        if type_ == 'echanger' and cat != 'Livres':
            raise forms.ValidationError(
                "L'option « À échanger » est réservée aux livres."
            )
        if cat == 'Livres' and prix and prix > 5000:
            raise forms.ValidationError(
                "Le prix d'un livre ne peut pas dépasser 5 000 FCFA."
            )
        return cleaned


class ArticlePhotoForm(forms.ModelForm):
    class Meta:
        model  = ArticlePhoto
        fields = ('image',)
        widgets = {
            'image': forms.FileInput(attrs={'accept': 'image/*', 'class': 'form-control'})
        }


# Formulaire multi-photos pour l'ajout d'article (jusqu'à 5)
PhotoFormSet = forms.inlineformset_factory(
    Article, ArticlePhoto,
    form=ArticlePhotoForm,
    extra=1,
    max_num=5,
    can_delete=True,
)


class DemandeEchangeForm(forms.ModelForm):
    """L'utilisateur propose son livre en échange avec une photo."""
    class Meta:
        model  = DemandeEchange
        fields = ('titre_livre', 'description_livre', 'photo_livre', 'message')
        widgets = {
            'titre_livre': forms.TextInput(attrs={
                'placeholder': 'Titre du livre que vous proposez'
            }),
            'description_livre': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'État, édition, auteur...'
            }),
            'message': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Message au vendeur (optionnel)'
            }),
        }
        labels = {
            'photo_livre': '📷 Photo de votre livre (obligatoire)',
        }

    def clean_photo_livre(self):
        photo = self.cleaned_data.get('photo_livre')
        if not photo:
            raise forms.ValidationError("Une photo de votre livre est obligatoire.")
        return photo


class DemandeArticleForm(forms.ModelForm):
    """L'utilisateur demande à l'admin d'ajouter un article."""
    class Meta:
        model  = DemandeArticle
        fields = ('nom_article', 'categorie', 'description', 'budget_max')
        widgets = {
            'nom_article': forms.TextInput(attrs={
                'placeholder': 'Ex: Livre « Le Monde de Sophie »'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Décrivez l\'article que vous recherchez...'
            }),
            'budget_max': forms.NumberInput(attrs={'min': 0, 'placeholder': '0 = flexible'}),
        }
        labels = {
            'budget_max': 'Budget maximum (FCFA)',
        }


class EvaluationForm(forms.ModelForm):
    class Meta:
        model  = Evaluation
        fields = ('note', 'commentaire')
        widgets = {
            'note': forms.RadioSelect(choices=[(i, f'{"⭐" * i}') for i in range(1, 6)]),
            'commentaire': forms.Textarea(attrs={'rows': 3}),
        }
