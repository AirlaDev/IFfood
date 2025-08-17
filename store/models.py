from django.db import models
from django.conf import settings
from restaurant.models import Produto 

class Pedido(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('em_preparo', 'Em Preparo'),
        ('saiu_para_entrega', 'Saiu para Entrega'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    )

    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    data_pedido = models.DateTimeField(auto_now_add=True)
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
    produto = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    data_adicionado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens do Pedido"
        unique_together = ('pedido', 'produto')

    def __str__(self):
        # CORREÇÃO AQUI: Lida com o caso do produto ser None
        if self.produto:
            return f"{self.quantidade}x {self.produto.nome} no Pedido #{self.pedido.id}"
        return f"{self.quantidade}x [Produto Removido] no Pedido #{self.pedido.id}"

    @property
    def subtotal(self):
        """ 
        Calcula o subtotal para este item (preço * quantidade).
        CORREÇÃO AQUI: Retorna 0 se o produto foi removido.
        """
        if self.produto and self.produto.preco is not None:
            return self.produto.preco * self.quantidade
        return 0