from django.core.paginator import Paginator

TEN_PAGES = 10


def padinator_page(queryset, request):
    paginator = Paginator(queryset, TEN_PAGES)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
