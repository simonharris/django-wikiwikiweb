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


def wikispace_required(view_func):

    def wrapper(request, *args, **kwargs):
        if not request.session.get('sess_space_key'):
            intermediate = (reverse('djwiki:space_select')
                            + '?next='
                            + request.get_full_path())
            return redirect(intermediate)
        return view_func(request, *args, **kwargs)

    return wrapper


class HomeView(generic.TemplateView):
    template_name = 'wiki/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['pages_created'] = WikiPage.objects.order_by('-created')[:ITEMS_PER_PAGE]
        context['pages_updated'] = WikiPage.objects.order_by('-updated')[:ITEMS_PER_PAGE]
        return context

    def get(self, request, *args, **kwargs):
        # Clear selected space   (TODO: decide whether this is actually helpful)
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

            # Display success dialogue if that's what just happened
            status_key = request.GET.get('success')
            context['status_key'] = status_key

            return self.render_to_response(context)
        except Http404:
            view = PageCreateView.as_view()
            return view(request, *args, **kwargs)


class PageArchiveView(generic.DetailView):

    # TODO: set Space into session?

    model = HistoricalWikiPage
    context_object_name = 'mypage'
    template_name = 'wiki/wiki_page_archive.html'

@method_decorator(login_required, name='dispatch')
@method_decorator(wikispace_required, name='dispatch')
class PageCreateView(generic.edit.CreateView):
    model = WikiPage
    context_object_name = 'mypage'
    template_name = 'wiki/wiki_page_create.html'

    form_class = PageCreateForm

    # TODO: this seems superfluous. Used in one place?
    def setup(self, request, *args, **kwargs):
        """Initialize attributes shared by all view methods"""

        space_key = request.session.get('sess_space_key')

        try:
            self.space = WikiSpace.objects.get(name=space_key)
        except:
            pass # TODO. But so far only happens if arrive at non-existent page, but with no Space in session

        return super(PageCreateView, self).setup(request, *args, **kwargs)


    # TODO: is this even necessary? Should always be in the URL, not the form
    # - and you don't want them to change it, bypassing existence checks. See #18
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
        """Add current space and user to new page"""

        form.instance.space = self.space
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super(PageCreateView, self).form_valid(form)


    def get_success_url(self):
        new_page_name = self.object.name
        return reverse('djwiki:page_view', kwargs={'pk': new_page_name}) + '?success=created'


@method_decorator(login_required, name='dispatch')
class PageEditView(generic.edit.UpdateView):
    model = WikiPage
    context_object_name = 'mypage'
    template_name = 'wiki/wiki_page_edit.html'
    form_class = PageEditForm

    def form_valid(self, form):
        """Add current space and user to new page"""

        form.instance.updated_by = self.request.user
        return super(PageEditView, self).form_valid(form)

    def get_success_url(self):
        new_page_name = self.object.name
        return reverse('djwiki:page_view', kwargs={'pk': new_page_name}) + '?success=updated'


@method_decorator(wikispace_required, name='dispatch')
class SearchView(generic.ListView):

    template_name = 'wiki/search.html'
    model = WikiPage
    context_object_name = 'pages_list'
    #paginate_by = ITEMS_PER_PAGE

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


class SpaceSelectView(generic.edit.FormView):

    form_class = SpaceSelectForm
    template_name = 'wiki/space_select.html'

    def form_valid(self, form):

        chosen_id = self.request.POST.get('space_choice')
        chosen_space = WikiSpace.objects.get(pk=chosen_id)
        self.request.session['sess_space_key'] = chosen_space.name

        return super().form_valid(form)

    def get_success_url(self):
        return self.request.POST.get('next')

    def get_context_data(self, **kwargs):
        context = super(SpaceSelectView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next')
        return context


@method_decorator(login_required, name='dispatch')
class MyView(generic.TemplateView):

    template_name = 'wiki/mywiki.html'


class UserView(generic.TemplateView):
    template_name = 'wiki/user.html'
