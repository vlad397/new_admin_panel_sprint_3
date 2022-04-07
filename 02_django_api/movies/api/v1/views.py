from django.contrib.postgres.aggregates import ArrayAgg
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from movies.models import Filmwork, PersonFilmWork


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self):
        roles = PersonFilmWork.Role
        return Filmwork.objects.prefetch_related('genres',
                                                 'persons').values().annotate(
            genres=ArrayAgg('genres__name', distinct=True),
            actors=ArrayAgg(
                'persons__full_name', distinct=True,
                filter=Q(personfilmwork__role__exact=roles.ACTOR.value)),
            directors=ArrayAgg(
                'persons__full_name', distinct=True,
                filter=Q(personfilmwork__role__exact=roles.DIRECTOR.value)),
            writers=ArrayAgg(
                'persons__full_name', distinct=True,
                filter=Q(personfilmwork__role__exact=roles.WRITER.value)))

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    model = Filmwork
    http_method_names = ['get']
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get('page')
        if page_number == 'last':
            page_number = paginator.page_range[-1]
        p_obj = paginator.get_page(page_number)
        prev = p_obj.previous_page_number() if p_obj.has_previous() else None
        next = p_obj.next_page_number() if p_obj.has_next() else None
        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': prev,
            'next': next,
            'results': list(p_obj),
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    model = Filmwork
    http_method_names = ['get']

    def get_context_data(self, *, object_list=None, **kwargs):
        return self.get_queryset().get(id=self.kwargs['pk'])
