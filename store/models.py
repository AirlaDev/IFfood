from django.db import models
from django.conf import settings
from restaurant.models import Produto # Importamos o modelo de Produto do outro app

class Pedido(models.Model):
    """
    Representa um carrinho de compras ou um pedido finalizado de um cliente.
    """
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('em_preparo', 'Em Preparo'),
        ('saiu_para_entrega', 'Saiu para Entrega'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    )

    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    data_pedido = models.DateTimeField(auto_now_add=True)
    # Este campo diferencia um carrinho ativo de um pedido finalizado.
    finalizado = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-data_pedido']

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.username}"

    @property
    def total_pedido(self):
        """ Calcula o valor total de todos os itens no pedido. """
        itens = self.itempedido_set.all()
        total = sum([item.subtotal for item in itens])
        return total
    
    @property
    def total_itens(self):
        """ Calcula a quantidade total de itens no pedido. """
        itens = self.itempedido_set.all()
        total = sum([item.quantidade for item in itens])
        return total


class ItemPedido(models.Model):
    """
    Representa um item específico (Produto) dentro de um Pedido.
    Esta é a sua tabela de relacionamento "Produto no Pedido".
    """
    produto = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    data_adicionado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens do Pedido"
        # Garante que não haja o mesmo produto duplicado no mesmo pedido
        unique_together = ('pedido', 'produto')

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} no Pedido #{self.pedido.id}"

    @property
    def subtotal(self):
        """ Calcula o subtotal para este item (preço * quantidade). """
        return self.produto.preco * self.quantidade