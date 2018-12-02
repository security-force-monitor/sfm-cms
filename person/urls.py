from django.conf.urls import url
from django.views.decorators.cache import cache_page

from person.views import PersonDetail, PersonCreateView, PersonEditBasicsView, \
    PersonEditPostingsView, PersonCreatePostingView, person_autocomplete, \
    PersonDeletePostingView

urlpatterns = [
    url(r'^create/$',
        PersonCreateView.as_view(),
        name="create-person"),
    url(r'create/posting/(?P<person_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        PersonCreatePostingView.as_view(),
        name='create-person-posting'),
    url(r'edit/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        PersonEditBasicsView.as_view(),
        name='edit-person'),
    url(r'edit/postings/(?P<person_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>\d+)/$',
        PersonEditPostingsView.as_view(),
        name='edit-person-postings'),
    url(r'delete/posting/(?P<person_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>\d+)/$',
        PersonDeletePostingView.as_view(),
        name='delete-person-posting'),
    url(r'^view/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        PersonDetail.as_view(),
        name="view-person"),
    url(r'autocomplete/$',
        person_autocomplete,
        name='person-autocomplete'),
]
