from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from .forms import ClienteCreationForm
from .models import Pedido, ItemPedido
from restaurant.models import Produto

# --- VIEWS DE AUTENTICAÇÃO (sem alterações) ---
def cadastro_cliente(request):
    if request.method == 'POST':
        form = ClienteCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('store:lista_produtos')
    else:
        form = ClienteCreationForm()
    return render(request, 'store/auth/cadastro.html', {'form': form})

def login_cliente(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('store:lista_produtos')
    else:
        form = AuthenticationForm()
    return render(request, 'store/auth/login.html', {'form': form})

@require_POST # Garante que o logout só pode ser feito via POST
def logout_cliente(request):
    logout(request)
    return redirect('store:lista_produtos')

# --- VIEWS DA LOJA (sem alterações na lista e no carrinho inicial) ---
def lista_produtos(request):
    produtos = Produto.objects.filter(ativo=True)
    return render(request, 'store/lista_produtos.html', {'produtos': produtos})

@login_required
def visualizar_carrinho(request):
    pedido, criado = Pedido.objects.get_or_create(cliente=request.user, finalizado=False)
    return render(request, 'store/carrinho.html', {'pedido': pedido})

# --- VIEWS DE AÇÕES (HTMX) ---
@require_POST
@login_required
def adicionar_ao_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    pedido, criado = Pedido.objects.get_or_create(cliente=request.user, finalizado=False)
    item, item_criado = ItemPedido.objects.get_or_create(pedido=pedido, produto=produto)
    if not item_criado:
        item.quantidade += 1
    item.save()
    return render(request, 'store/partials/contagem_carrinho.html', {'pedido': pedido})

# --- NOVA VIEW PARA ATUALIZAR QUANTIDADE ---
@require_POST
@login_required
def atualizar_carrinho(request, item_id):
    item = get_object_or_404(ItemPedido, id=item_id, pedido__cliente=request.user)
    action = request.POST.get('action') # Pega a ação ('inc' ou 'dec')

    if action == 'inc':
        item.quantidade += 1
        item.save()
    elif action == 'dec':
        item.quantidade -= 1
        if item.quantidade > 0:
            item.save()
        else:
            item.delete() # Remove o item se a quantidade chegar a zero

    pedido = item.pedido
    # Retorna o corpo do carrinho atualizado
    response = render(request, 'store/partials/corpo_carrinho.html', {'pedido': pedido})
    # Dispara o evento para atualizar o ícone do carrinho no header
    response['HX-Trigger'] = 'itemAdicionado'
    return response

# --- NOVA VIEW PARA REMOVER ITEM ---
@require_POST
@login_required
def remover_do_carrinho(request, item_id):
    item = get_object_or_404(ItemPedido, id=item_id, pedido__cliente=request.user)
    pedido = item.pedido
    item.delete()
    
    # Retorna o corpo do carrinho atualizado
    response = render(request, 'store/partials/corpo_carrinho.html', {'pedido': pedido})
    # Dispara o evento para atualizar o ícone do carrinho no header
    response['HX-Trigger'] = 'itemAdicionado'
    return response

# --- VIEW PARA PARTIAL HTMX (sem alterações) ---
def hx_contagem_carrinho(request):
    if request.user.is_authenticated:
        pedido, criado = Pedido.objects.get_or_create(cliente=request.user, finalizado=False)
        return render(request, 'store/partials/contagem_carrinho.html', {'pedido': pedido})
    return HttpResponse(status=204)

@require_POST
@login_required
def finalizar_pedido(request):
    pedido = get_object_or_404(Pedido, cliente=request.user, finalizado=False)
    
    # "Finaliza" o carrinho, transformando-o em um pedido real
    pedido.finalizado = True
    pedido.status = 'solicitado' # Novo status inicial!
    pedido.save()
    
    # Redireciona para uma futura página de "meus pedidos" ou de sucesso.
    # Por enquanto, voltamos para a lista de produtos.
    return redirect('store:lista_produtos')

@login_required
def meus_pedidos(request):
    # Busca todos os pedidos finalizados do usuário logado
    pedidos = Pedido.objects.filter(cliente=request.user, finalizado=True).order_by('-data_pedido')
    return render(request, 'store/meus_pedidos.html', {'pedidos': pedidos})