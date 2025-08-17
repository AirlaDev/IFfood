from django import forms
from .models import Produto

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        exclude = ['restaurante']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Pizza Margherita'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Molho de tomate, mozzarella e manjericão fresco'
            }),
            'preco': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 32.90'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch'
            }),
        }