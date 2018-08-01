# -*- coding: utf-8 -*-
import sys

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _, get_language

from django_date_extensions.fields import ApproximateDateFormField

from complex_fields.models import ComplexFieldContainer

from source.models import Source
from .models import Person, PersonName, PersonAlias, PersonGender, \
    PersonDivisionId, PersonDateOfDeath, PersonDateOfBirth, PersonExternalLink, \
    PersonDeceased, PersonBiography, PersonNotes


class GetOrCreateChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self,
                 queryset,
                 required=True,
                 widget=None,
                 label=None,
                 initial=None,
                 help_text='',
                 *args,
                 **kwargs):

        self.object_ref_pk = kwargs.pop('object_ref_pk')
        self.object_ref_model = kwargs.pop('object_ref_model')

        super().__init__(queryset,
                         required=required,
                         widget=widget,
                         label=label,
                         initial=initial,
                         help_text=help_text,
                         *args,
                         **kwargs)


    def clean(self, value):

        pks = []

        for v in value:
            try:
                queryset = super().clean([v])
                pks.append(v)
            except forms.ValidationError as e:
                object_ref = self.object_ref_model.objects.get(uuid=self.object_ref_pk)
                instance = self.queryset.model.objects.create(value=e.params['pk'],
                                                              object_ref=object_ref,
                                                              lang=get_language())
                pks.append(instance.id)

        return self.queryset.model.objects.filter(pk__in=pks)


class PersonForm(forms.ModelForm):

    object_type = 'person'

    # field name on person model, the ForeignKey model and if there are multiple
    # values

    edit_fields = [
        ('name', PersonName, False),
        ('aliases', PersonAlias, True),
        ('gender', PersonGender, False),
        ('division_id', PersonDivisionId, False),
        ('date_of_birth', PersonDateOfBirth, False),
        ('date_of_death', PersonDateOfDeath, False),
        ('deceased', PersonDeceased, False),
        ('biography', PersonBiography, False),
        ('notes', PersonNotes, False),
        ('external_links', PersonExternalLink, True),
    ]

    name = forms.CharField()
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female')], required=False)
    division_id = forms.CharField(required=False)
    date_of_birth = ApproximateDateFormField(required=False)
    date_of_death = ApproximateDateFormField(required=False)
    deceased = forms.BooleanField()
    biography = forms.CharField(required=False)
    notes = forms.CharField(required=False)

    class Meta:
        model = Person
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.post_data = dict(kwargs.pop('post_data'))
        object_ref_pk = kwargs.pop('object_ref_pk')
        super().__init__(*args, **kwargs)
        self.fields['aliases'] = GetOrCreateChoiceField(queryset=PersonAlias.objects.filter(object_ref__uuid=object_ref_pk),
                                                        required=False,
                                                        object_ref_pk=object_ref_pk,
                                                        object_ref_model=self._meta.model)
        self.fields['external_links'] = GetOrCreateChoiceField(queryset=PersonExternalLink.objects.filter(object_ref__uuid=object_ref_pk),
                                                               required=False,
                                                               object_ref_pk=object_ref_pk,
                                                               object_ref_model=self._meta.model)

    def clean(self):

        modified_fields = self.post_data.get('modified_fields')

        for field in self.fields:

            if isinstance(self.fields[field], forms.BooleanField):

                if field in modified_fields:
                    if self.post_data.get('{}_source'.format(field)):
                        value = True

                        # Clear out "field is required" validation error that
                        # happens when you toggle from True to False. If there is an
                        # error, we also know that the value should be False
                        try:
                            self.errors.pop(field)
                            value = False
                        except KeyError:
                            pass

                        self.cleaned_data[field] = value
                        self.post_data[field] = [value]
                else:
                    # The boolean fields are not actually required but Django
                    # forces them to be.
                    self.errors.pop(field)

            if field in modified_fields:

                try:
                    self.post_data['{}_source'.format(field)]
                except KeyError:
                    error = forms.ValidationError(_('"%(field_name)s" requires a new source'),
                                                code='invalid',
                                                params={'field_name': field})
                    self.add_error(field, error)

                # If the posted value is empty but there are sources, that means
                # that the user cleared out the value and gave evidence as to
                # why that was the case. Unfortunately, if the value is empty,
                # Django removes it from the POST data altogether (I guess it's
                # trying to do us a favor?). Anyways, we need to add that back
                # in so we can clear out the value from the field.

                if not self.post_data.get(field) and self.post_data.get('{}_source'.format(field)) is not None:
                    # If the field is a GetOrCreate field that means that we
                    # should make the value an empty list. Otherwise it should
                    # be None

                    if isinstance(self.fields[field], GetOrCreateChoiceField):
                        self.post_data[field] = []

                    else:
                        self.post_data[field] = None

    def save(self, commit=True):

        update_info = {}

        for field_name, field_model, multiple_values in self.edit_fields:

            if field_name in self.post_data.get('modified_fields'):

                new_source_ids = self.post_data.get('{}_source'.format(field_name))

                sources = Source.objects.filter(uuid__in=new_source_ids)

                field = ComplexFieldContainer.field_from_str_and_id(
                    'person', self.instance.id, field_name
                )

                existing_sources = field.get_sources()

                if existing_sources:
                    sources = sources | existing_sources

                confidence = field.get_confidence()

                update_value = self.cleaned_data[field_name]
                update_key = '{0}_{1}'.format(self.instance._meta.object_name, field_model._meta.object_name)

                update_info[update_key] = {
                    'sources': sources,
                    'confidence': confidence,
                }

                if multiple_values:
                    update_info[update_key]['values'] = update_value

                else:
                    update_info[update_key]['value'] = update_value

        if update_info:
            self.instance.update(update_info)
