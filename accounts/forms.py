from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.validators import RegexValidator
from .models import User, DemandeVerification


telephone_validator = RegexValidator(
    regex=r'^6[0-9]{8}$',
    message="Numéro invalide. Format attendu : 6XXXXXXXX (9 chiffres commençant par 6)"
)


class InscriptionForm(UserCreationForm):
    """Formulaire d'inscription complet."""
    first_name = forms.CharField(
        max_length=80, label="Prénom",
        widget=forms.TextInput(attrs={'placeholder': 'Votre prénom'})
    )
    last_name = forms.CharField(
        max_length=80, label="Nom de famille",
        widget=forms.TextInput(attrs={'placeholder': 'Votre nom'})
    )
    email = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(attrs={'placeholder': 'votre@email.com'})
    )
    telephone = forms.CharField(
        max_length=9, validators=[telephone_validator],
        label="Téléphone",
        widget=forms.TextInput(attrs={'placeholder': '6XXXXXXXX'})
    )
    ville = forms.CharField(
        max_length=100, label="Ville",
        widget=forms.TextInput(attrs={'placeholder': 'Yaoundé, Douala...'})
    )
    region = forms.ChoiceField(
        choices=[('', '-- Choisir une région --')] + User.REGION_CHOICES,
        label="Région"
    )

    class Meta:
        model  = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'telephone', 'ville', 'region', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_telephone(self):
        tel = self.cleaned_data['telephone']
        if User.objects.filter(telephone=tel).exists():
            raise forms.ValidationError("Ce numéro de téléphone est déjà utilisé.")
        return tel


class ConnexionForm(AuthenticationForm):
    """Formulaire de connexion — accepte username OU email."""
    username = forms.CharField(
        label="Nom d'utilisateur ou email",
        widget=forms.TextInput(attrs={'placeholder': "Nom d'utilisateur ou email"})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
    )

    def clean(self):
        username_or_email = self.cleaned_data.get('username', '').strip()

        # Si c'est un email, on cherche le username correspondant
        if '@' in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                self.cleaned_data['username'] = user_obj.username
            except User.DoesNotExist:
                raise forms.ValidationError("Aucun compte trouvé avec cet email.")

        return super().clean()


class ProfilForm(forms.ModelForm):
    """Modification du profil utilisateur (incluant photo de profil)."""

    class Meta:
        model  = User
        fields = ('first_name', 'last_name', 'email', 'telephone',
                  'ville', 'region', 'bio', 'photo_profil')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Décrivez-vous en quelques mots...'}),
        }
        labels = {
            'photo_profil': 'Photo de profil',
            'bio': 'Biographie',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['photo_profil'].required = False
        self.fields['photo_profil'].widget.attrs.update({
            'accept': 'image/*',
            'class': 'form-control'
        })


class DemandeVerificationForm(forms.ModelForm):
    """Formulaire de demande de certification envoyé à l'admin."""

    class Meta:
        model  = DemandeVerification
        fields = ('message', 'document')
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Expliquez pourquoi vous souhaitez être certifié(e)...'
            }),
        }
        labels = {
            'message':  "Votre message à l'admin",
            'document': 'Document justificatif (optionnel)',
        }