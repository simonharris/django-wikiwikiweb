from django.forms import ModelForm

from .models import WikiPage


class PageCreateForm(ModelForm):

    class Meta:
        model = WikiPage
        fields = ['name', 'content', 'edit_reason']


class PageEditForm(ModelForm):

    def __init__(self, *args, **kwargs):
        """There MUST be a simpler way to override a simple input value"""

        initial = kwargs.get('initial', {})
        initial['edit_reason'] = ''
        kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    class Meta:
        model = WikiPage
        fields = ['content', 'edit_reason']
