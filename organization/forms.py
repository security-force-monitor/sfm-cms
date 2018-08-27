from django import forms

from django.conf import settings
from django_date_extensions.fields import ApproximateDateFormField
from django.utils.translation import ugettext as _

from django_date_extensions.fields import ApproximateDateFormField

from sfm_pc.forms import BaseEditForm, GetOrCreateChoiceField, BasePostingsForm

from membershipperson.models import MembershipPersonMember
from person.models import Person

from composition.models import Composition, CompositionParent, \
    CompositionChild, CompositionRealStart, CompositionStartDate, \
    CompositionEndDate, CompositionOpenEnded, CompositionClassification

from .models import Organization, OrganizationName, OrganizationAlias, \
    OrganizationClassification, OrganizationDivisionId, OrganizationHeadquarters, \
    OrganizationFirstCitedDate, OrganizationLastCitedDate, OrganizationRealStart, \
    OrganizationOpenEnded


class OrganizationBasicsForm(BaseEditForm):
    class Meta:
        model = Organization
        fields = '__all__'

    edit_fields = [
        ('name', OrganizationName, False),
        ('aliases', OrganizationAlias, True),
        ('classification', OrganizationClassification, True),
        ('division_id', OrganizationDivisionId, False),
        ('firstciteddate', OrganizationFirstCitedDate, False),
        ('lastciteddate', OrganizationLastCitedDate, False),
        ('realstart', OrganizationRealStart, False),
        ('open_ended', OrganizationOpenEnded, False),
    ]

    name = forms.CharField()
    division_id = forms.CharField(required=False)
    firstciteddate = ApproximateDateFormField(required=False)
    lastciteddate = ApproximateDateFormField(required=False)
    realstart = forms.BooleanField()
    open_ended = forms.ChoiceField(choices=[('Y', 'Yes'), ('N', 'No'), ('E', 'Last cited date is termination date')], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['aliases'] = GetOrCreateChoiceField(queryset=OrganizationAlias.objects.filter(object_ref__uuid=self.object_ref_pk),
                                                        required=False,
                                                        object_ref_pk=self.object_ref_pk,
                                                        object_ref_model=self._meta.model)
        self.fields['classification'] = GetOrCreateChoiceField(queryset=OrganizationClassification.objects.filter(object_ref__uuid=self.object_ref_pk),
                                                               required=False,
                                                               object_ref_pk=self.object_ref_pk,
                                                               object_ref_model=self._meta.model)


class OrganizationRelationshipsForm(BaseEditForm):
    class Meta:
        model = Composition
        fields = '__all__'

    edit_fields = [
        ('parent', CompositionParent, False),
        ('child', CompositionChild, False),
        ('realstart', CompositionRealStart, False),
        ('startdate', CompositionStartDate, False),
        ('enddate', CompositionEndDate, False),
        ('open_ended', CompositionOpenEnded, False),
        ('classification', CompositionClassification, False),
    ]

    realstart = forms.BooleanField()
    startdate = ApproximateDateFormField(required=False)
    enddate = ApproximateDateFormField(required=False)
    open_ended = forms.ChoiceField(choices=[('Y', 'Yes'), ('N', 'No'), ('E', 'Last cited date is termination date')], required=False)
    parent = forms.ModelChoiceField(queryset=Organization.objects.all(), required=False)
    child = forms.ModelChoiceField(queryset=Organization.objects.all(), required=False)
    classification = forms.CharField(required=False)

    def clean(self):

        self._validate_complex_field(self.instance.parent, 'parent')
        self._validate_complex_field(self.instance.child, 'child')

        if self.errors.get('parent') and self.post_data.get('child_source'):
            self.post_data['parent_source'] = self.post_data['child_source']
            self.cleaned_data['parent'] = Organization.objects.get(id=self.post_data['parent'][0])
            del self.errors['parent']

        if self.errors.get('child') and self.post_data.get('parent_source'):
            self.post_data['child_source'] = self.post_data['parent_source']
            self.cleaned_data['child'] = Organization.objects.get(id=self.post_data['child'][0])
            del self.errors['child']

        super().clean()


class OrganizationPersonnelForm(BasePostingsForm):
    edit_fields = BasePostingsForm.edit_fields + [('person', MembershipPersonMember, False)]

    person = forms.ModelChoiceField(queryset=Person.objects.all())
