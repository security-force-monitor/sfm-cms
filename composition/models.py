from django.db import models
from django.utils.translation import ugettext as _

from django_date_extensions.fields import ApproximateDateField

from organization.models import Organization
from complex_fields.model_decorators import versioned, sourced
from complex_fields.models import ComplexField, ComplexFieldContainer
from complex_fields.base_models import BaseModel


class Composition(models.Model, BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = ComplexFieldContainer(self, CompositionParent)
        self.child = ComplexFieldContainer(self, CompositionChild)
        self.startdate = ComplexFieldContainer(self, CompositionStartDate)
        self.enddate = ComplexFieldContainer(self, CompositionEndDate)
        self.classification = ComplexFieldContainer(self, CompositionClassification)

        self.open_ended = ComplexFieldContainer(self, CompositionOpenEnded)

        self.complex_fields = [self.parent, self.child, self.startdate,
                               self.enddate, self.classification]

        self.required_fields = [
            "Composition_CompositionParent", "Composition_CompositionChild"
        ]

    def get_value(self):
        return '{0} parent of {1}'.format(self.parent.get_value(),
                                          self.child.get_value())


@versioned
@sourced
class CompositionParent(ComplexField):
    object_ref = models.ForeignKey(Composition)
    value = models.ForeignKey(Organization, related_name='child_organization')
    field_name = _("Parent organization")


@versioned
@sourced
class CompositionChild(ComplexField):
    object_ref = models.ForeignKey(Composition)
    value = models.ForeignKey(Organization, related_name='parent_organization')
    field_name = _("Child organization")


@versioned
@sourced
class CompositionStartDate(ComplexField):
    object_ref = models.ForeignKey(Composition)
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("Start date")


@versioned
@sourced
class CompositionEndDate(ComplexField):
    object_ref = models.ForeignKey(Composition)
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("End date")


@versioned
@sourced
class CompositionClassification(ComplexField):
    object_ref = models.ForeignKey(Composition)
    value = models.ForeignKey("Classification", default=None, blank=True,
                              null=True)
    field_name = _("Classification")


class Classification(models.Model):
    value = models.TextField()

    def __str__(self):
        return self.value


@versioned
class CompositionOpenEnded(ComplexField):
    object_ref = models.ForeignKey(Composition)
    value = models.NullBooleanField(default=None, blank=True, null=True)
    field_name = _("Open ended")
