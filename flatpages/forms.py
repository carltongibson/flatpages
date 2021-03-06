from django import forms
from django.conf import settings
from django.utils.translation import ugettext, ugettext_lazy as _
from .models import FlatPage


class FlatpageForm(forms.ModelForm):
    url = forms.RegexField(label=_("URL"), max_length=100, regex=r'^[-\w/\.~]+$',
        help_text=_("Example: '/about/contact/'. Make sure to have leading"
                    " and trailing slashes."),
        error_messages={
            "invalid": _("This value must contain only letters, numbers,"
                         " dots, underscores, dashes, slashes or tildes."),
        },
    )

    class Meta:
        model = FlatPage
        fields = '__all__'

    def clean_url(self):
        url = self.cleaned_data['url']
        if not url.startswith('/'):
            raise forms.ValidationError(
                ugettext("URL is missing a leading slash."),
                code='missing_leading_slash',
            )
# Commenting to out because IN GENERAL I like APPEND_SLASH but don't want to enforce that here.
#
# TODO: Decide what to do here.
#         if (settings.APPEND_SLASH and
#                 'django.middleware.common.CommonMiddleware' in settings.MIDDLEWARE_CLASSES and
#                 not url.endswith('/')):
#             raise forms.ValidationError(
#                 ugettext("URL is missing a trailing slash."),
#                 code='missing_trailing_slash',
#             )
        return url

    def clean(self):
        url = self.cleaned_data.get('url', None)
        sites = self.cleaned_data.get('sites', None)

        same_url = FlatPage.objects.filter(url=url)
        if self.instance.pk:
            same_url = same_url.exclude(pk=self.instance.pk)

        if sites and same_url.filter(sites__in=sites).exists():
            for site in sites:
                if same_url.filter(sites=site).exists():
                    raise forms.ValidationError(
                        _('Flatpage with url %(url)s already exists for site %(site)s'),
                        code='duplicate_url',
                        params={'url': url, 'site': site},
                    )

        return super(FlatpageForm, self).clean()
