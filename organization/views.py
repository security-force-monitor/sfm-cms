import os
import json
from io import StringIO

from django.views.generic import DetailView, FormView
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.db import connection
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext as _

from emplacement.models import Emplacement

from association.models import Association

from composition.models import Composition

from organization.forms import OrganizationBasicsForm, \
    OrganizationRelationshipsForm, OrganizationPersonnelForm, \
    OrganizationEmplacementForm, OrganizationAssociationForm, \
    OrganizationCreateBasicsForm, OrganizationCreateRelationshipsForm, \
    OrganizationCreatePersonnelForm, OrganizationCreateEmplacementForm, \
    OrganizationCreateAssociationForm, DownloadForm
from organization.models import Organization, OrganizationAlias, \
    OrganizationDivisionId

from membershipperson.models import MembershipPerson

from sfm_pc.templatetags.countries import country_name
from sfm_pc.base_views import BaseUpdateView, BaseCreateView


class OrganizationDetail(DetailView):
    model = Organization
    template_name = 'organization/view.html'
    slug_field = 'uuid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Generate link to download a CSV of this record
        params = '?download_etype=Organization&entity_id={0}'.format(str(context['organization'].uuid))

        context['download_url'] = reverse('download') + params

        # Commanders of this unit
        context['person_members'] = []
        person_members = context['organization'].membershippersonorganization_set.all()
        for membership in person_members:
            context['person_members'].append(membership.object_ref)

        # Organizational members of this unit
        context['org_members'] = []
        org_members = context['organization'].membershiporganizationorganization_set.all()
        if org_members:
            org_members = (mem.object_ref for mem in org_members)
            context['org_members'] = org_members

        # Other units that this unit is a member of
        context['memberships'] = []
        memberships = context['organization'].membershiporganizationmember_set.all()
        if memberships:
            memberships = (mem.object_ref for mem in memberships)
            context['memberships'] = memberships

        # Child units
        context['subsidiaries'] = []
        children = context['organization'].child_organization.all()
        for child in children:
            context['subsidiaries'].append(child.object_ref)

        # Incidents that this unit perpetrated
        context['events'] = []
        events = context['organization'].violationperpetratororganization_set.all()
        for event in events:
            context['events'].append(event.object_ref)

        context['sites'] = []
        emplacements = tuple(context['organization'].emplacements)
        context['emplacements'] = (em.object_ref for em in emplacements)
        for emplacement in emplacements:
            context['sites'].append(emplacement.object_ref.site.get_value().value)

        context['areas'] = []
        associations = tuple(context['organization'].associations)
        context['associations'] = (ass.object_ref for ass in associations)
        for association in associations:
            geom = association.object_ref.area.get_value().value.geometry
            area_obj = {
                'geom': geom,
                'name': association.object_ref.area.get_value().value.name
            }
            context['areas'].append(area_obj)

        context['parents'] = []
        context['parents_list'] = []
        parents = context['organization'].parent_organization.all()
        # "parent" is a CompositionChild
        for parent in parents:

            context['parents'].append(parent.object_ref.parent.get_value().value)

            org_data = {'when': '', 'url': ''}

            when = None
            if parent.object_ref.enddate.get_value():
                # Make the query using the raw date string, to accomodate
                # fuzzy dates
                when = repr(parent.object_ref.enddate.get_value().value)
                org_data['when'] = when

                # Display a formatted date
                org_data['display_date'] = str(parent.object_ref.enddate.get_value())

            kwargs = {'org_id': str(context['organization'].uuid)}
            ajax_route = 'command-chain'
            if when:
                kwargs['when'] = when
                ajax_route = 'command-chain-bounded'

            command_chain_url = reverse(ajax_route, kwargs=kwargs)

            org_data['url'] = command_chain_url

            context['parents_list'].append(org_data)

        context['versions'] = context['organization'].getVersions()

        return context


class OrganizationEditView(BaseUpdateView):
    model = Organization
    slug_field = 'uuid'
    slug_field_kwarg = 'slug'
    context_object_name = 'organization'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['organization'] = self.get_reference_organization()

        first_composition = context['organization'].child_organization.first()

        if not first_composition:
            first_composition = context['organization'].parent_organization.first()

        first_personnel = context['organization'].membershippersonorganization_set.first()

        first_emplacement = context['organization'].emplacements.first()
        first_association = context['organization'].associations.first()

        context['first_personnel'] = getattr(first_personnel, 'object_ref', None)
        context['first_composition'] = getattr(first_composition, 'object_ref', None)
        context['first_emplacement'] = getattr(first_emplacement, 'object_ref', None)
        context['first_association'] = getattr(first_association, 'object_ref', None)

        return context

    def get_success_url(self):
        uuid = self.kwargs[self.slug_field_kwarg]
        return reverse('view-organization', kwargs={'slug': uuid})


class OrganizationEditBasicsView(OrganizationEditView):
    template_name = 'organization/edit-basics.html'
    form_class = OrganizationBasicsForm

    def get_reference_organization(self):
        return Organization.objects.get(uuid=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['basics'] = True

        return context

    def get_success_url(self):
        organization_id = self.kwargs[self.slug_field_kwarg]

        if self.request.POST.get('_continue'):
            return reverse('edit-organization', kwargs={'slug': organization_id})
        else:
            return super().get_success_url()

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['organization_id'] = self.kwargs['slug']
        return form_kwargs


class OrganizationCreateBasicsView(BaseCreateView):
    model = Organization
    slug_field = 'uuid'
    slug_field_kwarg = 'slug'
    context_object_name = 'organization'
    template_name = 'organization/create-basics.html'
    form_class = OrganizationCreateBasicsForm

    def form_valid(self, form):
        form.save(commit=True)
        return HttpResponseRedirect(reverse('view-organization',
                                    kwargs={'slug': form.object_ref.uuid}))

    def get_success_url(self):
        # This method doesn't ever really get called but since Django does not
        # seem to recognize when we place a get_absolute_url method on the model
        # and some way of determining where to redirect after the form is saved
        # is required, here ya go. The redirect actually gets handled in the
        # form_valid method above.
        return '{}?entity_type=Organization'.format(reverse('search'))


class OrganizationEditRelationshipsView(OrganizationEditView):
    template_name = 'organization/edit-relationships.html'
    form_class = OrganizationRelationshipsForm
    model = Composition
    context_object_name = 'current_composition'
    slug_field_kwarg = 'pk'

    def get_reference_organization(self):
        return Organization.objects.get(uuid=self.kwargs['organization_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        parents = Q(compositionparent__value=context['organization'])
        children = Q(compositionchild__value=context['organization'])

        context['compositions'] = Composition.objects.filter(parents | children)

        return context

    def get_success_url(self):
        organization_id = self.kwargs['organization_id']
        pk = self.kwargs['pk']

        if self.request.POST.get('_continue'):
            return reverse('edit-organization-relationships',
                           kwargs={'organization_id': organization_id,
                                   'pk': pk})
        else:
            return reverse('view-organization', kwargs={'slug': organization_id})


class OrganizationCreateRelationshipsView(BaseCreateView):
    template_name = 'organization/create-relationships.html'
    form_class = OrganizationCreateRelationshipsForm
    model = Composition
    context_object_name = 'current_composition'
    slug_field_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization'] = Organization.objects.get(uuid=self.kwargs['organization_id'])

        parents = Q(compositionparent__value=context['organization'])
        children = Q(compositionchild__value=context['organization'])

        context['compositions'] = Composition.objects.filter(parents | children)

        return context

    def get_success_url(self):
        return reverse('edit-organization', kwargs={'slug': self.kwargs['organization_id']})


class OrganizationEditPersonnelView(OrganizationEditView):
    model = MembershipPerson
    template_name = 'organization/edit-personnel.html'
    form_class = OrganizationPersonnelForm
    context_object_name = 'current_membership'
    slug_field_kwarg = 'organization_id'

    def get_reference_organization(self):
        return Organization.objects.get(uuid=self.kwargs['organization_id'])

    def get_success_url(self):
        organization_id = self.kwargs['organization_id']
        pk = self.kwargs['pk']

        if self.request.POST.get('_continue'):
            return reverse('edit-organization-personnel',
                           kwargs={'organization_id': organization_id,
                                   'pk': pk})
        else:
            return reverse('view-organization', kwargs={'slug': organization_id})

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['organization_id'] = self.kwargs['organization_id']
        return form_kwargs


class OrganizationCreatePersonnelView(BaseCreateView):
    model = MembershipPerson
    template_name = 'organization/create-personnel.html'
    form_class = OrganizationCreatePersonnelForm
    context_object_name = 'current_membership'
    slug_field_kwarg = 'organization_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization'] = Organization.objects.get(uuid=self.kwargs['organization_id'])
        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['organization_id'] = self.kwargs['organization_id']
        return form_kwargs

    def get_success_url(self):
        return reverse('edit-organization', kwargs={'slug': self.kwargs['organization_id']})


class OrganizationEditEmplacementView(OrganizationEditView):
    model = Emplacement
    template_name = 'organization/edit-emplacement.html'
    form_class = OrganizationEmplacementForm
    context_object_name = 'current_emplacement'
    slug_field_kwarg = 'pk'

    def get_reference_organization(self):
        return Organization.objects.get(uuid=self.kwargs['organization_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['emplacements'] = [e.object_ref for e in context['organization'].emplacements]
        context['associations'] = [e.object_ref for e in context['organization'].associations]

        return context

    def get_success_url(self):
        organization_id = self.kwargs['organization_id']
        pk = self.kwargs['pk']

        if self.request.POST.get('_continue'):
            return reverse('edit-organization-emplacement',
                           kwargs={'organization_id': organization_id,
                                   'pk': pk})
        else:
            return reverse('view-organization', kwargs={'slug': organization_id})

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['organization_id'] = self.kwargs['organization_id']
        return form_kwargs


class OrganizationCreateEmplacementView(BaseCreateView):
    model = Emplacement
    template_name = 'organization/create-emplacement.html'
    form_class = OrganizationCreateEmplacementForm
    slug_field_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization'] = Organization.objects.get(uuid=self.kwargs['organization_id'])
        context['emplacements'] = [e.object_ref for e in context['organization'].emplacements]
        context['associations'] = [e.object_ref for e in context['organization'].associations]
        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['organization_id'] = self.kwargs['organization_id']
        return form_kwargs

    def get_success_url(self):
        return reverse('edit-organization', kwargs={'slug': self.kwargs['organization_id']})


class OrganizationEditAssociationView(OrganizationEditView):
    model = Association
    template_name = 'organization/edit-association.html'
    form_class = OrganizationAssociationForm
    context_object_name = 'current_association'
    slug_field_kwarg = 'pk'

    def get_reference_organization(self):
        return Organization.objects.get(uuid=self.kwargs['organization_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['emplacements'] = [e.object_ref for e in context['organization'].emplacements]
        context['associations'] = [e.object_ref for e in context['organization'].associations]

        return context

    def get_success_url(self):
        organization_id = self.kwargs['organization_id']
        pk = self.kwargs['pk']

        if self.request.POST.get('_continue'):
            return reverse('edit-organization-association',
                           kwargs={'organization_id': organization_id,
                                   'pk': pk})
        else:
            return reverse('view-organization', kwargs={'slug': organization_id})


class OrganizationCreateAssociationView(BaseCreateView):
    model = Association
    template_name = 'organization/create-association.html'
    form_class = OrganizationCreateAssociationForm
    slug_field_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization'] = Organization.objects.get(uuid=self.kwargs['organization_id'])
        context['emplacements'] = [e.object_ref for e in context['organization'].emplacements]
        context['associations'] = [e.object_ref for e in context['organization'].associations]
        return context

    def get_success_url(self):
        return reverse('edit-organization', kwargs={'slug': self.kwargs['organization_id']})


class OrganizationDownloadPicker(FormView):
    template_name = 'organization/download-picker.html'
    form_class = DownloadForm
    success_url = reverse_lazy('organization-download')

    def form_valid(self, form):

        download_type = form.cleaned_data['download_type']
        division_id = form.cleaned_data['division_id']

        sql_path = os.path.join(settings.BASE_DIR,
                                'organization',
                                'sql',
                                'organization_{}.sql'.format(download_type))

        with open(sql_path) as f:
            sql = f.read()

        download_name = 'organization_{}_{}'.format(download_type,
                                                    timezone.now().isoformat())

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(download_name)

        with connection.cursor() as cursor:
            copy = '''
                COPY ({}) TO STDOUT WITH CSV HEADER FORCE QUOTE *
            '''.format(sql)

            try:
                copy = copy % division_id
            except TypeError:
                pass

            cursor.copy_expert(copy, response)

        return response


def organization_autocomplete(request):
    term = request.GET.get('q')

    response = {
        'results': []
    }

    if term:
        organizations = Organization.objects.filter(organizationname__value__icontains=term)[:10]

        for organization in organizations:
            result = {
                'id': organization.id,
                'text': organization.name.get_value().value,
                'aliases': organization.alias_list,
                'country': None,
            }

            if organization.division_id.get_value():
                result['country'] = country_name(organization.division_id.get_value().value)

            response['results'].append(result)

    return HttpResponse(json.dumps(response), content_type='application/json')
