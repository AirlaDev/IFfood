from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
# ADICIONE A LINHA ABAIXO
from django.http import JsonResponse
from .models import Produto
from .forms import ProdutoForm
from store.models import Pedido
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count, Sum
from store.models import ItemPedido
import json

# --- AUTENTICAÇÃO (sem alterações) ---
class CustomLoginView(LoginView):
    template_name = 'restaurant/login.html'

# --- CRUD DE PRODUTOS (COM JAVASCRIPT/AJAX) ---

@login_required
def visualizar_produto(request):
    produtos = Produto.objects.all().order_by('nome')
    context = {'produtos': produtos}
    return render(request, 'restaurant/product_list.html', context)

@login_required
def adicionar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response['HX-Refresh'] = 'true'
            return response
    else:
        form = ProdutoForm()
    context = {'form': form, 'page_title': 'Adicionar Produto'}
    return render(request, 'restaurant/partials/_form_partial.html', context)

@login_required
def editar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response['HX-Refresh'] = 'true'
            return response
    else:
        form = ProdutoForm(instance=produto)
    context = {'form': form, 'page_title': 'Editar Produto'}
    return render(request, 'restaurant/partials/_form_partial.html', context)

@login_required
def deletar_produto(request, pk):
    # Busca o produto ou retorna um erro 404 se não existir
    produto = get_object_or_404(Produto, pk=pk)

    # Se a requisição for do tipo POST (envio do formulário de exclusão)
    if request.method == 'POST':
        produto.delete()
        # Prepara uma resposta vazia (status 204)
        response = HttpResponse(status=204)
        # Adiciona o cabeçalho que o HTMX usa para recarregar a página
        response['HX-Refresh'] = 'true'
        return response

    # Se a requisição for GET, apenas mostra o modal de confirmação
    context = {'object': produto}
    return render(request, 'restaurant/partials/_delete_partial.html', context)


@login_required
def gestao_pedidos(request):
    pedidos_solicitados = Pedido.objects.filter(finalizado=True, status='solicitado').order_by('data_pedido')
    pedidos_em_preparo = Pedido.objects.filter(finalizado=True, status='em_preparo').order_by('data_pedido')
    pedidos_em_entrega = Pedido.objects.filter(finalizado=True, status='saiu_para_entrega').order_by('data_pedido')
    pedidos_finalizados = Pedido.objects.filter(finalizado=True, status='entregue').order_by('-data_pedido')[:15]

    # Soma os pedidos que ainda não foram finalizados para o card de "Total"
    total_pedidos = pedidos_solicitados.count() + pedidos_em_preparo.count() + pedidos_em_entrega.count()

    context = {
        'pedidos_solicitados': pedidos_solicitados,
        'pedidos_em_preparo': pedidos_em_preparo,
        'pedidos_em_entrega': pedidos_em_entrega,
        'pedidos_finalizados': pedidos_finalizados,
        'total_pedidos': total_pedidos,
    }
    return render(request, 'restaurant/gestao_pedidos.html', context)

@login_required
def detalhes_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    return render(request, 'restaurant/partials/_modal_detalhes_pedido.html', {'pedido': pedido})

def _recarregar_kanban(request):
    pedidos_solicitados = Pedido.objects.filter(finalizado=True, status='solicitado').order_by('data_pedido')
    pedidos_em_preparo = Pedido.objects.filter(finalizado=True, status='em_preparo').order_by('data_pedido')
    pedidos_em_entrega = Pedido.objects.filter(finalizado=True, status='saiu_para_entrega').order_by('data_pedido')
    pedidos_finalizados = Pedido.objects.filter(finalizado=True, status='entregue').order_by('-data_pedido')[:10]
    context = {
        'pedidos_solicitados': pedidos_solicitados,
        'pedidos_em_preparo': pedidos_em_preparo,
        'pedidos_em_entrega': pedidos_em_entrega,
        'pedidos_finalizados': pedidos_finalizados,
    }
    return render(request, 'restaurant/partials/_kanban_board_content.html', context)

@login_required
def aceitar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.status = 'em_preparo'
    pedido.save()
    return _recarregar_kanban(request)

@login_required
def marcar_como_em_entrega(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.status = 'saiu_para_entrega'
    pedido.save()
    return _recarregar_kanban(request)

@login_required
def marcar_como_finalizado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.status = 'entregue'
    pedido.save()
    return _recarregar_kanban(request)

@login_required
def dashboard(request):
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    # Pedidos por período
    pedidos_hoje = Pedido.objects.filter(data_pedido__date=today).count()
    pedidos_mes = Pedido.objects.filter(data_pedido__year=current_year, data_pedido__month=current_month).count()
    pedidos_ano = Pedido.objects.filter(data_pedido__year=current_year).count()

    # Produtos mais pedidos (Top 5)
    produtos_mais_pedidos = ItemPedido.objects.values('produto__nome') \
        .annotate(total_vendido=Sum('quantidade')) \
        .order_by('-total_vendido')[:5]

    # Prepara dados para o gráfico
    chart_labels = [item['produto__nome'] for item in produtos_mais_pedidos]
    chart_data = [item['total_vendido'] for item in produtos_mais_pedidos]

    context = {
        'pedidos_hoje': pedidos_hoje,
        'pedidos_mes': pedidos_mes,
        'pedidos_ano': pedidos_ano,
        'produtos_mais_pedidos': produtos_mais_pedidos,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'restaurant/dashboard.html', context)