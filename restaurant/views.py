from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
# ADICIONE A LINHA ABAIXO
from django.http import JsonResponse
from .models import Produto
from .forms import ProdutoForm
from store.models import Pedido

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
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    
    form = ProdutoForm()
    context = {
        'form': form,
        'page_title': 'Adicionar Novo Produto',
        'action_url': request.path
    }
    return render(request, 'restaurant/partials/_form_partial.html', context)

@login_required
def editar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    
    form = ProdutoForm(instance=produto)
    context = {
        'form': form,
        'page_title': 'Editar Produto',
        'action_url': request.path
    }
    return render(request, 'restaurant/partials/_form_partial.html', context)

@login_required
def deletar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        produto.delete()
        return JsonResponse({'success': True})
    
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