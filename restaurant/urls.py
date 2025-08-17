from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'restaurant'

urlpatterns = [
    
    # Autenticação
    path('login/', views.CustomLoginView.as_view(), name='login'),
    # NOVA ROTA DE CADASTRO
    path('cadastro/', views.cadastro_restaurante, name='cadastro'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # CRUD de Produtos (URLs simplificadas)
    path('produtos/', views.visualizar_produto, name='visualizar_produto'),
    path('produtos/adicionar/', views.adicionar_produto, name='adicionar_produto'),
    path('produtos/editar/<int:pk>/', views.editar_produto, name='editar_produto'),
    path('produtos/deletar/<int:pk>/', views.deletar_produto, name='deletar_produto'),

    # PAINEL DE GESTÃO DE PEDIDOS (sem alterações aqui)
    path('pedidos/', views.gestao_pedidos, name='gestao_pedidos'),
    
    # URLS PARA HTMX do Kanban (ainda necessárias para o painel de pedidos)
    path('pedidos/detalhes/<int:pedido_id>/', views.detalhes_pedido, name='detalhes_pedido'),
    path('pedidos/aceitar/<int:pedido_id>/', views.aceitar_pedido, name='aceitar_pedido'),
    path('pedidos/em-entrega/<int:pedido_id>/', views.marcar_como_em_entrega, name='marcar_como_em_entrega'),
    path('pedidos/finalizado/<int:pedido_id>/', views.marcar_como_finalizado, name='marcar_como_finalizado'),

    # Adicione esta linha no início do urlpatterns
    path('dashboard/', views.dashboard, name='dashboard'),

    # NOVAS ROTAS
    path('pedidos/recusar/<int:pedido_id>/', views.recusar_pedido, name='recusar_pedido'),
    path('pedidos/limpar-finalizados/', views.limpar_finalizados, name='limpar_finalizados'),
]