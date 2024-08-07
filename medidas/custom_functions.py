from django.db.models.query import QuerySet
from django.db.models import Q

# Hace la busqueda en el modelo especificado con las palabras clave y en los campos especificados
# Esta busqueda es la misma que usa el admin de django


def django_admin_keyword_search(model, keywords, search_fields):
    all_queries = None

    for keyword in keywords.split(' '):
        keyword_query = None

        for field in search_fields:
            each_query = Q(**{field+'__icontains': keyword})

            if not keyword_query:
                keyword_query = each_query
            else:
                keyword_query = keyword_query | each_query

        if not all_queries:
            all_queries = keyword_query
        else:
            all_queries = all_queries & keyword_query

    result_set = model.objects.filter(all_queries).distinct()

    return result_set


def isOnlyOneTrue(*args):
    result = False
    for v in args:
        if result and v:
            return False
        result = result or v
    return result
