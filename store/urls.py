from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Autenticação
    path('cadastro/', views.cadastro_cliente, name='cadastro'),
    path('login/', views.login_cliente, name='login'),
    path('sair/', views.logout_cliente, name='logout'),

    # Loja
    path('', views.lista_produtos, name='lista_produtos'),
    path('carrinho/', views.visualizar_carrinho, name='visualizar_carrinho'),
    
    # Ações do Carrinho (HTMX)
    path('adicionar-ao-carrinho/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    
    # URLS ATUALIZADAS E NOVAS
    path('atualizar-carrinho/<int:item_id>/', views.atualizar_carrinho, name='atualizar_carrinho'),
    path('remover-do-carrinho/<int:item_id>/', views.remover_do_carrinho, name='remover_do_carrinho'),
    
    # Partials para HTMX
    path('hx-contagem-carrinho/', views.hx_contagem_carrinho, name='hx_contagem_carrinho'),

    path('finalizar-pedido/', views.finalizar_pedido, name='finalizar_pedido'),

    # PÁGINA DE MEUS PEDIDOS
    path('meus-pedidos/', views.meus_pedidos, name='meus_pedidos'),
]