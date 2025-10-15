from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product
from django.core.paginator import Paginator


@login_required
def product_list(request):
    qs = Product.objects.select_related('category').all()
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(name__icontains=q)
    paginator = Paginator(qs, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'catalog/product_list.html', {'products': page_obj.object_list, 'page_obj': page_obj, 'q': q})


@login_required
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'catalog/product_detail.html', {'product': product})

# Create your views here.
