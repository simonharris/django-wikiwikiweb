from django.forms import HiddenInput, ModelForm, Textarea

from .models import WikiPage


class PageCreateForm(ModelForm):

    # TODO: "creating blah in lalala"

    class Meta:
        model = WikiPage
        fields = ['name', 'content', 'edit_reason']
        widgets = {
             'content': Textarea(attrs={'label': 'Page Content:'}),
             #'space': HiddenInput(),
        }


class PageEditForm(ModelForm):

    class Meta:
        model = WikiPage
        fields = ['content', 'space', 'edit_reason']
        widgets = {
             'content': Textarea(attrs={'label': 'Page Content:'}),
             # # TODO: do I even need this now? It won't change
             'space': HiddenInput(),
        }