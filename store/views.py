from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from .forms import ClienteCreationForm
from .models import Pedido, ItemPedido
from restaurant.models import Produto
from django.db.models import Q

# --- VIEWS DE AUTENTICAÇÃO ---
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

@require_POST
def logout_cliente(request):
    logout(request)
    return redirect('store:lista_produtos')

# --- VIEWS DA LOJA ---
def lista_produtos(request):
    # Pega o termo de busca da URL (ex: ?q=pizza)
    query = request.GET.get('q')
    
    # Começa com todos os produtos ativos
    produtos = Produto.objects.filter(ativo=True)
    
    # Se um termo de busca foi enviado, filtra a lista de produtos
    if query:
        # Filtra por nome OU descrição que contenha o termo da busca (case-insensitive)
        produtos = produtos.filter(
            Q(nome__icontains=query) |
            Q(descricao__icontains=query)
        )
        
    context = {
        'produtos': produtos,
        'search_term': query, # Envia o termo de volta para o template
    }
    return render(request, 'store/lista_produtos.html', context)

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
    
    # CORREÇÃO: Renderiza o novo template parcial completo
    return render(request, 'store/partials/_carrinho_icone.html', {'pedido': pedido})


@require_POST
@login_required
def atualizar_carrinho(request, item_id):
    item = get_object_or_404(ItemPedido, id=item_id, pedido__cliente=request.user)
    action = request.POST.get('action')
    if action == 'inc':
        item.quantidade += 1
        item.save()
    elif action == 'dec':
        item.quantidade -= 1
        if item.quantidade > 0:
            item.save()
        else:
            item.delete()
    response = render(request, 'store/partials/corpo_carrinho.html', {'pedido': item.pedido})
    response['HX-Trigger'] = 'itemAdicionado'
    return response

@require_POST
@login_required
def remover_do_carrinho(request, item_id):
    item = get_object_or_404(ItemPedido, id=item_id, pedido__cliente=request.user)
    pedido = item.pedido
    item.delete()
    response = render(request, 'store/partials/corpo_carrinho.html', {'pedido': pedido})
    response['HX-Trigger'] = 'itemAdicionado'
    return response

def hx_contagem_carrinho(request):
    if request.user.is_authenticated:
        pedido, criado = Pedido.objects.get_or_create(cliente=request.user, finalizado=False)
        # CORREÇÃO: Renderiza o novo template parcial completo
        return render(request, 'store/partials/_carrinho_icone.html', {'pedido': pedido})
    
    # Renderiza o estado vazio para usuários não logados
    return render(request, 'store/partials/_carrinho_icone.html', {'pedido': None})




# --- VIEWS DE PEDIDOS ---
@require_POST
@login_required
def finalizar_pedido(request):
    pedido = get_object_or_404(Pedido, cliente=request.user, finalizado=False)
    if pedido.total_itens > 0:
        pedido.finalizado = True
        pedido.status = 'solicitado' # Status inicial do pedido
        pedido.save()
        # Redireciona para a nova página de acompanhamento
        return redirect('store:acompanhar_pedido', pedido_id=pedido.id)
    # Se o carrinho estiver vazio, volta para a lista de produtos
    return redirect('store:lista_produtos')

@login_required
def meus_pedidos(request):
    pedidos = Pedido.objects.filter(cliente=request.user, finalizado=True).order_by('-data_pedido')
    return render(request, 'store/meus_pedidos.html', {'pedidos': pedidos})

# NOVA VIEW PARA ACOMPANHAR O PEDIDO
@login_required
def acompanhar_pedido(request, pedido_id):
    # Garante que o usuário só pode ver seus próprios pedidos
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    return render(request, 'store/acompanhar_pedido.html', {'pedido': pedido})

# VIEW PARA renderizar o "mini-template" que atualiza a cada 5s o status do pedido
@login_required
def hx_acompanhar_pedido_status(request, pedido_id):
    # Esta view serve apenas o pedaço do template com a timeline
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    return render(request, 'store/partials/_timeline_status.html', {'pedido': pedido})