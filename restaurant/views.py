from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from .models import Produto
from .forms import ProdutoForm
from store.models import Pedido # Importa o modelo Pedido do app 'store'

# --- AUTENTICAÇÃO DO RESTAURANTE ---
# A classe que estava faltando provavelmente é esta:
class CustomLoginView(LoginView):
    template_name = 'restaurant/login.html'

# --- CRUD DE PRODUTOS ---
@login_required
def visualizar_produto(request):
    produtos = Produto.objects.all().order_by('nome')
    context = {'produtos': produtos}
    return render(request, 'restaurant/product_list.html', context)

@login_required
def adicionar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('restaurant:visualizar_produto')
    else:
        form = ProdutoForm()
    context = {'form': form, 'page_title': 'Adicionar Produto'}
    return render(request, 'restaurant/product_form.html', context)

@login_required
def editar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response['HX-Refresh'] = 'true'
            return response
    else:
        form = ProdutoForm(instance=produto)
    context = {'form': form, 'page_title': 'Editar Produto'}
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'restaurant/partials/_form_partial.html', context)
    else:
        return render(request, 'restaurant/product_form.html', context)

@login_required
def deletar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        produto.delete()
        response = HttpResponse(status=204)
        response['HX-Refresh'] = 'true'
        return response
    context = {'object': produto}
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'restaurant/partials/_delete_partial.html', context)
    else:
        return render(request, 'restaurant/product_confirm_delete.html', context)

# --- GESTÃO DE PEDIDOS ---
@login_required
def gestao_pedidos(request):
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

@require_POST
@login_required
def aceitar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.status = 'em_preparo'
    pedido.save()
    return _recarregar_kanban(request)

@require_POST
@login_required
def marcar_como_em_entrega(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.status = 'saiu_para_entrega'
    pedido.save()
    return _recarregar_kanban(request)

@require_POST
@login_required
def marcar_como_finalizado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.status = 'entregue'
    pedido.save()
    return _recarregar_kanban(request)