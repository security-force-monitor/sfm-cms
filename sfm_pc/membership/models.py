from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from django.db.models import Max

from django_date_extensions.fields import ApproximateDateField

from complex_fields.model_decorators import (versioned, translated, sourced,
                                             sourced_optional)
from complex_fields.models import (ComplexField, ComplexFieldContainer,
                                   ComplexFieldListContainer)
from complex_fields.base_models import BaseModel
from person.models import Person
from source.models import Source
from organization.models import Organization


class Membership(models.Model, BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.personmember = ComplexFieldContainer(self, MembershipPersonMember)
        self.organizationmember = ComplexFieldContainer(self, MembershipOrganizationMember)
        self.organization = ComplexFieldContainer(self, MembershipOrganization)
        self.role = ComplexFieldContainer(self, MembershipRole)
        self.title = ComplexFieldContainer(self, MembershipTitle)
        self.rank = ComplexFieldContainer(self, MembershipRank)
        self.realstart = ComplexFieldContainer(self, MembershipRealStart)
        self.realend = ComplexFieldContainer(self, MembershipRealEnd)
        self.startcontext = ComplexFieldContainer(self, MembershipStartContext)
        self.endcontext = ComplexFieldContainer(self, MembershipEndContext)
        self.firstciteddate = ComplexFieldContainer(self, MembershipFirstCitedDate)
        self.lastciteddate = ComplexFieldContainer(self, MembershipLastCitedDate)

        self.complex_fields = [self.personmember, self.organizationmember,
                               self.organization, self.role, self.title, self.rank,
                               self.realstart, self.realend, self.startcontext,
                               self.endcontext, self.firstciteddate, self.lastciteddate]

        self.required_fields = [
            "Membership_MembershipPerson",
            "Membership_MembershipOrganization",
        ]


    @classmethod
    def from_id(cls, id_):
        try:
            membership = cls.objects.get(id=id_)
            return membership
        except cls.DoesNotExist:
            return None

    def validate(self, dict_values):
        errors = {}

        person_member = dict_values.get("Membership_MembershipPersonMember")
        organization_member = dict_values.get("Membership_MembershipOrganizationMember")
        if ((person_member.get("value", "") == "" and
             organization_member.get("value", "") == "")):
            errors['Membership_MembershipPersonMember'] = (
                _("One, and only one, person or organization must be choose as a member"))

        elif (person_member.get("value", "") != ""):
            sources = person_member.get("sources")
            if not len(sources):
                errors["Membership_MembershipPersonMember"] = ("Sources are " +
                        "required to update this field")
        elif (organization_member.get("value", "") != ""):
            sources = organization_member.get("sources")
            if not len(sources):
                errors["Membership_MembershipOrganizationMember"] = ("Sources are " +
                        "required to update this field")

        first_cited = dict_values.get("Membership_MembershipFirstCitedDate")
        last_cited = dict_values.get("Membership_MembershipLastCitedDate")
        if (first_cited and first_cited.get('value') != "" and
                last_cited and last_cited.get("value") != "" and
                first_cited.get('value') >= last_cited.get('value')):
            errors["Membership_MembershipFirstCitedDate"] = (
                "The first cited date must be before the last cited date"
            )

        real_start = dict_values.get("Membership_MembershipRealStart")
        real_end = dict_values.get("Membership_MembershipRealEnd")
        if( real_start.get("value") == 'True' and not len(real_start.get('sources'))):
            errors['Membership_MembershipRealStart'] = ("Sources are required " +
                                                        "to update this field")
        if( real_end.get("value") == 'True' and not len(real_end.get('sources'))):
            errors['Membership_MembershipRealEnd'] = ("Sources are required " +
                                                        "to update this field")

        (base_errors, values) = super().validate(dict_values)
        errors.update(base_errors)

        return (errors, values)


    @classmethod
    def create(cls, dict_values, lang=get_language()):
        membership = cls()
        membership.update(dict_values, lang)
        return membership

    @classmethod
    def search(cls, terms):
        order_by = terms.get('orderby')
        if not order_by:
            order_by = 'membershiprole__value'
        elif order_by in ['title']:
            order_by = 'membership' + order_by + '__value'

        direction = terms.get('direction')
        if not direction:
            direction = 'ASC'

        dirsym = ''
        if direction == 'DESC':
            dirsym = '-'

        membership_query = (Membership.objects
                            .annotate(Max(order_by))
                            .order_by(dirsym + order_by + "__max"))

        role = terms.get("role")
        if role:
            membership_query = membership_query.filter(membershiprole__value=role)

        rank = terms.get("rank")
        if rank:
            membership_query = membership_query.filter(membershiprank__value=rank)

        title = terms.get("title")
        if title:
            membership_query = membership_query.filter(membershiptitle__value=title)

        startdate_year = terms.get('startdate_year')
        if startdate_year:
            membership_query = membership_query.filter(
                membershipfirstciteddate__value__startswith=startdate_year
            )

        startdate_month = terms.get('startdate_month')
        if startdate_month:
            membership_query = membership_query.filter(
                membershipfirstciteddate__value__contains="-" + startdate_month + "-"
            )

        startdate_day = terms.get('startdate_day')
        if startdate_day:
            membership_query = membership_query.filter(
                membershipfirstciteddate__value__endswith=startdate_day
            )

        enddate_year = terms.get('enddate_year')
        if enddate_year:
            membership_query = membership_query.filter(
                membershiplastciteddate__value__startswith=enddate_year
            )

        enddate_month = terms.get('enddate_month')
        if enddate_month:
            membership_query = membership_query.filter(
                membershiplastciteddate__value__contains="-" + enddate_month + "-"
            )

        enddate_day = terms.get('enddate_day')
        if enddate_day:
            membership_query = membership_query.filter(
                membershiplastciteddate__value__endswith=enddate_day
            )

        return membership_query


@versioned
@sourced_optional
class MembershipPersonMember(ComplexField):
    object_ref = models.ForeignKey('Membership')
    value = models.ForeignKey(Person, default=None, blank=True, null=True)
    field_name = _("Person member")


@versioned
@sourced_optional
class MembershipOrganizationMember(ComplexField):
    object_ref = models.ForeignKey('Membership')
    value = models.ForeignKey(Organization, default=None, blank=True, null=True)
    field_name = _("Organization member")


@versioned
@sourced
class MembershipOrganization(ComplexField):
    object_ref = models.ForeignKey('Membership')
    value = models.ForeignKey(Organization)
    field_name = _("Organization")


@versioned
@sourced
class MembershipRole(ComplexField):
    object_ref = models.ForeignKey('Membership')
    value = models.ForeignKey('Role', default=None, blank=True, null=True)
    field_name = _("Role")


@translated
@versioned
@sourced
class MembershipTitle(ComplexField):
    object_ref = models.ForeignKey('Membership')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Title")


@versioned
@sourced
class MembershipRank(ComplexField):
    object_ref = models.ForeignKey('Membership')
    value = models.ForeignKey('Rank', default=None, blank=True, null=True)
    field_name = _("Rank")


@versioned
@sourced
class MembershipFirstCitedDate(ComplexField):
    object_ref = models.ForeignKey('Membership')
    value = ApproximateDateField()
    field_name = _("First cited date")


@versioned
@sourced
class MembershipLastCitedDate(ComplexField):
    object_ref = models.ForeignKey('Membership')
    value = ApproximateDateField()
    field_name = _("Last cited date")


@versioned
@sourced_optional
class MembershipRealStart(ComplexField):
    object_ref = models.ForeignKey('Membership')
    value = models.BooleanField(default=None)
    field_name = _("Real start date")


@versioned
@sourced_optional
class MembershipRealEnd(ComplexField):
    object_ref = models.ForeignKey('Membership')
    value = models.BooleanField(default=None)
    field_name = _("Real end date")


@versioned
@sourced
class MembershipStartContext(ComplexField):
    object_ref = models.ForeignKey('Membership')
    value = models.ForeignKey('Context')
    field_name = _("Start context")


@versioned
@sourced
class MembershipEndContext(ComplexField):
    object_ref = models.ForeignKey('Membership')
    value = models.ForeignKey('Context')
    field_name = _("End context")


class Role(models.Model):
    value = models.TextField()

    @classmethod
    def get_role_list(cls):
        roles = cls.objects.all()
        roles = [
            role.value
            for role in roles
        ]

        return roles

    def __str__(self):
        return self.value


class Rank(models.Model):
    value = models.TextField()

    def __str__(self):
        return self.value


class Context(models.Model):
    value = models.TextField()

    def __str__(self):
        return self.value
