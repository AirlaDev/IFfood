from django.db import models
from django.conf import settings

class Produto(models.Model):    
    nome = models.CharField(max_length=100, verbose_name="Nome")
    descricao = models.TextField(verbose_name="Descrição")
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço")    
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['nome']

    def __str__(self):
        return self.nome