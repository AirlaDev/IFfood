from django import forms
from .models import Produto
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RestauranteCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        # Marca o usuário como staff para dar acesso ao painel
        user.is_staff = True
        if commit:
            user.save()
        return user

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto        
        fields = ['nome', 'descricao', 'preco', 'ativo', 'imagem']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'preco': forms.NumberInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),           
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }