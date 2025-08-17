from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'restaurant' # <<<--- ADICIONE ESTA LINHA

urlpatterns = [
    # Autenticação
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # CRUD de Produtos
    path('', views.visualizar_produto, name='visualizar_produto'),
    path('produtos/adicionar/', views.adicionar_produto, name='adicionar_produto'),
    path('produtos/editar/<int:pk>/', views.editar_produto, name='editar_produto'),
    path('produtos/deletar/<int:pk>/', views.deletar_produto, name='deletar_produto'),

    # NOVO PAINEL DE GESTÃO DE PEDIDOS
    path('pedidos/', views.gestao_pedidos, name='gestao_pedidos'),
    
    # URLS PARA HTMX (MODAL E AÇÕES)
    path('pedidos/detalhes/<int:pedido_id>/', views.detalhes_pedido, name='detalhes_pedido'),
    path('pedidos/aceitar/<int:pedido_id>/', views.aceitar_pedido, name='aceitar_pedido'),

    path('pedidos/em-entrega/<int:pedido_id>/', views.marcar_como_em_entrega, name='marcar_como_em_entrega'),
    path('pedidos/finalizado/<int:pedido_id>/', views.marcar_como_finalizado, name='marcar_como_finalizado'),
]