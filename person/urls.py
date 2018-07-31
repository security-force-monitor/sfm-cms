from django.conf.urls import url
from django.views.decorators.cache import cache_page

from person.views import PersonDetail, PersonCreateView, PersonEditView

urlpatterns = [
    url(r'^create/$',
        PersonCreateView.as_view(),
        name="create-person"),
    url(r'edit/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', PersonEditView.as_view(), name='edit-person'),
    url(r'^view/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        cache_page(60 * 60 * 24)(PersonDetail.as_view()),
        name="view-person"),
]
