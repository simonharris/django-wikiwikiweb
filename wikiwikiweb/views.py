from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic

from .forms import *
from .models import *

ITEMS_PER_PAGE = 10


class HomeView(generic.TemplateView):
    template_name = 'wiki/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['pages_created'] = WikiPage.objects.order_by('-created')[:ITEMS_PER_PAGE]
        context['pages_updated'] = WikiPage.objects.order_by('-updated')[:ITEMS_PER_PAGE]
        return context

    def get(self, request, *args, **kwargs):
        # Clear selected space
        request.session['sess_space_key'] = None
        return super().get(request, *args, **kwargs)


class PageView(generic.DetailView):
    model = WikiPage
    context_object_name = 'mypage'
    template_name = 'wiki/wiki_page.html'

    def dispatch(self, request, *args, **kwargs ):
        try:
            # Don't fully understand why this is so wordy, but it seems to be needed
            self.object = super().get_object()
            context = self.get_context_data(object=self.object)

            # TODO: some sort of constant for these key strings
            request.session['sess_space_key'] = self.object.space.name

            # Display edit success dialogue if that's what just happened
            if request.GET.get('win') == 'yes':
                context['success_msg'] = 'wikipage successfully updated'

            return self.render_to_response(context)
        except Http404:
            view = PageCreateView.as_view()
            return view(request, *args, **kwargs)


class PageArchiveView(generic.DetailView):

    # TODO: set Space into session?

    model = HistoricalWikiPage
    context_object_name = 'mypage'
    template_name = 'wiki/wiki_page_archive.html'


class PageCreateView(generic.edit.CreateView):
    model = WikiPage
    context_object_name = 'mypage'
    template_name = 'wiki/wiki_page_create.html'

    form_class = PageCreateForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def setup(self, request, *args, **kwargs):
        """Initialize attributes shared by all view methods"""

        space_key = request.session.get('sess_space_key')

        try:
            self.space = WikiSpace.objects.get(name=space_key)
        except:
            pass # TODO. But so far only happens if arrive at non-existent page, but with no Space in session

        return super(PageCreateView, self).setup(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):

        defaults = {
            'name': self.kwargs['pk'],
        }

        form = self.form_class(initial=defaults)
        context = {
            'form': form
        }
        return render(request, self.template_name, context)


    def form_valid(self, form):
        """Add current space to new page"""

        # Maybe some checking my be needed here
        form.instance.space = self.space
        return super(PageCreateView, self).form_valid(form)


    def get_success_url(self):
        new_page_name = self.object.name
        return reverse('wiki:page_view', kwargs={'pk': new_page_name}) + '?win=yes'


class PageEditView(generic.edit.UpdateView):
    model = WikiPage
    context_object_name = 'mypage'
    template_name = 'wiki/wiki_page_edit.html'

    form_class = PageEditForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    # TODO: set Space into session?

    def get_success_url(self):
        new_page_name = self.object.name
        return reverse('wiki:page_view', kwargs={'pk': new_page_name}) + '?win=yes'


class SearchView(generic.ListView):

    template_name = 'wiki/search.html'
    model = WikiPage
    context_object_name = 'pages_list'
    #paginate_by = ITEMS_PER_PAGE


    def get(self, request):
        """Enforce session key for Space is set"""

        # TODO: see if can move to annotation
        search_space = request.session.get('sess_space_key')

        if search_space == None:
            # This doesn't work yet, need full 'next' URL
            to_url = reverse('wiki:space_select') + '?' + request.GET.urlencode()
            return redirect(to_url)

        return super().get(self, request)


    def get_queryset(self): #
        # TODO: needs checking for empty
        search_string = self.request.GET.get('q')
        search_space = self.request.session.get('sess_space_key')

        return WikiPage.objects.filter(
            Q(space__name=search_space) &
            (Q(name__icontains=search_string) | Q(content__icontains=search_string)),
        )


    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)

        # Add query string if present
        if self.request.GET.get('q'):
            # TODO: nb. context.update
            context['search_query'] = self.request.GET.get('q')

        return context


class SpaceView(generic.DetailView):
    model = WikiSpace
    slug_field = 'name'
    context_object_name = 'myspace'
    template_name = 'wiki/space.html'

    def get(self, request, *args, **kwargs):
        # Would already have 404d if string is not a valid space
        request.session['sess_space_key'] = kwargs['slug']
        return super().get(request, *args, **kwargs)

# TODO
class SpaceSelectView(generic.TemplateView):
    template_name = 'wiki/space_select.html'


class MyView(generic.TemplateView):
    template_name = 'wiki/mywiki.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class UserView(generic.TemplateView):
    template_name = 'wiki/user.html'
