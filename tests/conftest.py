# -*- coding: utf-8 -*-

import os
import subprocess

import pytest

from django.contrib.auth.models import User

from organization.models import Organization, OrganizationAlias, OrganizationClassification
from person.models import Person, PersonAlias, PersonExternalLink
from violation.models import Violation
from composition.models import Composition
from emplacement.models import Emplacement
from association.models import Association
from membershiporganization.models import MembershipOrganization
from membershipperson.models import MembershipPerson
from source.models import Source, AccessPoint
from location.models import Location


@pytest.fixture
def user():
    return User.objects.create(username='testuser',
                               first_name='Test',
                               last_name='User',
                               email='test@test.com',
                               password='test123')


@pytest.fixture
def sources(user):
    sources = []

    for index in range(5):
        source = Source.objects.create(title='Test {}'.format(index),
                                       publication='Publication {}'.format(index),
                                       publication_country='United States',
                                       published_on='2018-01-01',
                                       source_url='https://test.com/test-{}'.format(index),
                                       user=user)
        sources.append(source)

    return sources


@pytest.fixture
def access_points(user, sources):
    access_points = []

    for source in sources:
        for index in range(5):
            access_point = AccessPoint.objects.create(page_number='p10{}'.format(index),
                                                      accessed_on='2018-12-12',
                                                      archive_url='https://web.archive.org/https://test.com/test-{}'.format(index),
                                                      source=source,
                                                      user=user)
            access_points.append(access_point)

    return access_points


@pytest.fixture
def new_access_points(user, sources):
    access_points = []

    for source in sources:
        for index in range(5):
            access_point = AccessPoint.objects.create(page_number='p20{}'.format(index),
                                                      accessed_on='2017-12-12',
                                                      archive_url='https://web.archive.org/https://test.com/test-{}'.format(index),
                                                      source=source,
                                                      user=user)
            access_points.append(access_point)

    return access_points


@pytest.fixture
def location_adminlevel1():
    return Location.objects.create(id=5572040,
                                   name='Túxpam',
                                   division_id='ocd-division/country:mx',
                                   feature_type='relation')


@pytest.fixture
def location_adminlevel2():
    return Location.objects.create(id=2415761,
                                   name='Veracruz',
                                   division_id='ocd-division/country:mx',
                                   feature_type='relation')

@pytest.fixture
def location_node(location_adminlevel1, location_adminlevel2):

    return Location.objects.create(id=472257682,
                                   name='Túxpam de Rodríguez Cano, Veracruz',
                                   division_id='ocd-division/country:mx',
                                   feature_type='node',
                                   adminlevel1=location_adminlevel1,
                                   adminlevel2=location_adminlevel2)


@pytest.fixture
def location_relation(location_adminlevel1, location_adminlevel2):
    return Location.objects.create(id=5996623,
                                   name='Hpasawng Township, Kayah',
                                   division_id='ocd-division/country:mm',
                                   adminlevel1=location_adminlevel1,
                                   adminlevel2=location_adminlevel2)


@pytest.fixture
def organization_aliases(access_points):
    for index in range(2):
        return OrganizationAlias.objects.create(value='Alias {}'.format(index),
                                                accesspoints=access_points,
                                                )


@pytest.fixture
def base_organizations(access_points):

    organizations = []

    for index in range(3):

        org = {
            'Organization_OrganizationName': {
                'sources': access_points,
                'value': 'Test organization {}'.format(index),
                'confidence': '1',
            },
            'Organization_OrganizationDivisionId': {
                'sources': access_points,
                'value': 'ocd-division/country:us',
                'confidence': '1',
            }
        }

        organization = Organization.create(org)

        organizations.append(organization)

    return organizations


@pytest.fixture
def organization_aliases(base_organizations):

    aliases = []

    for organization in base_organizations:
        for index in range(2):
            alias = OrganizationAlias.objects.create(value='Alias {}'.format(index),
                                                     object_ref=organization,
                                                     lang='en')
            for access_point in organization.name.get_value().accesspoints.all():
                alias.accesspoints.add(access_point)
                alias.sources.add(access_point.source)

            aliases.append(alias)

    return aliases


@pytest.fixture
def organization_classifications(base_organizations):

    classifications = []

    for organization in base_organizations:
        for index in range(2):
            classification = OrganizationClassification.objects.create(value='Classification {}'.format(index),
                                                              object_ref=organization,
                                                              lang='en')
            for access_point in organization.name.get_value().accesspoints.all():
                classification.accesspoints.add(access_point)
                classification.sources.add(access_point.source)

            classifications.append(classification)

    return classifications


@pytest.fixture
def organizations(base_organizations,
                  organization_aliases,
                  organization_classifications,
                  access_points):

    organizations = []

    for organization in base_organizations:

        org_info = {
            'Organization_OrganizationFirstCitedDate': {
                'sources': access_points,
                'value': '2017-01-01',
                'confidence': '2',
            },
            'Organization_OrganizationLastCitedDate': {
                'sources': access_points,
                'value': '2018-01-01',
                'confidence': '1',
            },
            'Organization_OrganizationRealStart': {
                'value': False
            },
            'Organization_OrganizationOpenEnded': {
                'value': 'Y',
                'sources': access_points,
                'confidence': '2',
            }
        }

        organization.update(org_info)

        organization.published = True
        organization.save()

        organizations.append(organization)

    return organizations


@pytest.fixture
def composition(organizations, access_points):
    parent, middle, child = organizations

    comp_info = {
        'Composition_CompositionParent': {
            'sources': access_points,
            'value': parent,
            'confidence': '2'
        },
        'Composition_CompositionChild': {
            'sources': access_points,
            'value': middle,
            'confidence': '1',
        },
        'Composition_CompositionRealStart': {
            'value': False,
        },
        'Composition_CompositionStartDate': {
            'value': '2018-01-02',
            'confidence': '2',
            'sources': access_points,
        },
        'Composition_CompositionEndDate': {
            'value': '2018-03-01',
            'confidence': '1',
            'sources': access_points,
        },
        'Composition_CompositionOpenEnded': {
            'value': 'N',
            'confidence': '1',
            'sources': access_points,
        },
        'Composition_CompositionClassification': {
            'value': 'Command',
            'confidence': '2',
            'sources': access_points,
        }
    }

    Composition.create(comp_info)

    comp_info['Composition_CompositionParent']['value'] = middle
    comp_info['Composition_CompositionChild']['value'] = child

    Composition.create(comp_info)


@pytest.fixture
def emplacement(organizations, location_node, access_points):
    for organization in organizations:
        emp_info = {
            'Emplacement_EmplacementOrganization': {
                'value': organization,
                'sources': access_points,
                'confidence': '3'
            },
            'Emplacement_EmplacementStartDate': {
                'value': '2012-06-01',
                'confidence': '2',
                'sources': access_points,
            },
            'Emplacement_EmplacementEndDate': {
                'value': '2013-03-02',
                'confidence': '1',
                'sources': access_points,
            },
            'Emplacement_EmplacementRealStart': {
                'value': True
            },
            'Emplacement_EmplacementSite': {
                'value': location_node,
                'confidence': '2',
                'sources': access_points,
            },
            'Emplacement_EmplacementOpenEnded': {
                'value': 'Y',
                'confidence': '1',
                'sources': access_points,
            },
        }

        Emplacement.create(emp_info)


@pytest.fixture
def association(organizations, location_relation, access_points):

    for organization in organizations:
        ass_info = {
            'Association_AssociationRealStart': {
                'value': False
            },
            'Association_AssociationStartDate': {
                'value': '2016-08-01',
                'confidence': '1',
                'sources': access_points,
            },
            'Association_AssociationEndDate': {
                'value': '2017-10-23',
                'confidence': '2',
                'sources': access_points,
            },
            'Association_AssociationOrganization': {
                'value': organization,
                'confidence': '1',
                'sources': access_points,
            },
            'Association_AssociationArea': {
                'value': location_relation,
                'confidence': '1',
                'sources': access_points,
            },
            'Association_AssociationOpenEnded': {
                'value': 'E',
                'confidence': '1',
                'sources': access_points,
            }
        }

        Association.create(ass_info)


@pytest.fixture
def membership_organization(organizations, access_points):
    member, _, parent = organizations

    mem_info = {
        'MembershipOrganization_MembershipOrganizationMember': {
            'value': member,
            'sources': access_points,
            'confidence': '1'
        },
        'MembershipOrganization_MembershipOrganizationOrganization': {
            'value': parent,
            'sources': access_points,
            'confidence': '1'
        },
        'MembershipOrganization_MembershipOrganizationFirstCitedDate': {
            'value': '2002-01-01',
            'sources': access_points,
            'confidence': '1'
        },
        'MembershipOrganization_MembershipOrganizationLastCitedDate': {
            'value': '2003-01-01',
            'sources': access_points,
            'confidence': '1'
        },
        'MembershipOrganization_MembershipOrganizationRealStart': {
            'value': False,
        },
        'MembershipOrganization_MembershipOrganizationRealEnd': {
            'value': True,
        },
    }

    MembershipOrganization.create(mem_info)


@pytest.fixture
def full_organizations(organizations,
                       composition,
                       emplacement,
                       association,
                       membership_organization):

    return organizations


@pytest.fixture
def base_people(access_points):
    people = []

    for index in range(3):
        person = {
            'Person_PersonName': {
                'value': 'Test person {}'.format(index),
                'sources': access_points,
                'confidence': '1'
            },
            'Person_PersonDivisionId':{
                'value': 'ocd-division/country:us',
                'sources': access_points,
                'confidence': '2',
            }
        }

        people.append(Person.create(person))

    return people


@pytest.fixture
def people(base_people, access_points):
    # self.name = ComplexFieldContainer(self, PersonName)
    # self.aliases = ComplexFieldListContainer(self, PersonAlias)
    # self.division_id = ComplexFieldContainer(self, PersonDivisionId)
    # self.gender = ComplexFieldContainer(self, PersonGender)
    # self.date_of_birth = ComplexFieldContainer(self, PersonDateOfBirth)
    # self.date_of_death = ComplexFieldContainer(self, PersonDateOfDeath)
    # self.deceased = ComplexFieldContainer(self, PersonDeceased)
    # self.biography = ComplexFieldContainer(self, PersonBiography)
    # self.notes = ComplexFieldContainer(self, PersonNotes)
    # self.external_links = ComplexFieldListContainer(self, PersonExternalLink)
    for person in base_people:
        for index in range(2):
            alias = PersonAlias.objects.create(value='Alias {}'.format(index),
                                               lang='en',
                                               object_ref=person)

            alias.accesspoints.set(access_points)

            link = PersonExternalLink.objects.create(value='http://personblog.com/test-{}'.format(index),
                                                     lang='en',
                                                     object_ref=person)
            link.accesspoints.set(access_points)

        person_info = {
            'Person_PersonDivisionId': {
                'value': 'ocd-division/country:us',
                'sources': access_points,
                'confidence': '1'
            },
            'Person_PersonGender': {
                'value': 'Male',
                'sources': access_points,
                'confidence': '1'
            },
            'Person_PersonDateOfBirth': {
                'value': '2018-01-01',
                'sources': access_points,
                'confidence': '1'
            },
            'Person_PersonDateOfDeath': {
                'value': '2018-02-01',
                'sources': access_points,
                'confidence': '1'
            },
            'Person_PersonDeceased': {
                'value': True,
                'sources': access_points,
                'confidence': '1'
            },
            'Person_PersonBiography': {
                'value': 'This guy is great',
                'sources': access_points,
                'confidence': '1'
            },
            'Person_PersonNotes': {
                'value': 'Super great',
                'sources': access_points,
                'confidence': '1'
            },
        }

        person.update(person_info)

    return base_people


@pytest.fixture
def membership_person(access_points, people, organizations):

    memberships = []

    for member in people[:2]:
        mem_info = {
            'MembershipPerson_MembershipPersonMember': {
                'value': member,
                'sources': access_points,
                'confidence': '1',
            },
            'MembershipPerson_MembershipPersonOrganization': {
                'value': organizations[0],
                'sources': access_points,
                'confidence': '1',
            },
            'MembershipPerson_MembershipPersonRole': {
                'value': 'Honcho',
                'sources': access_points,
                'confidence': '1',
            },
            'MembershipPerson_MembershipPersonRank': {
                'value': 'Commander',
                'sources': access_points,
                'confidence': '1',
            },
            'MembershipPerson_MembershipPersonTitle': {
                'value': 'Big Chief',
                'sources': access_points,
                'confidence': '1',
            },
            'MembershipPerson_MembershipPersonRealStart': {
                'value': False,
            },
            'MembershipPerson_MembershipPersonRealEnd': {
                'value': False,
            },
            'MembershipPerson_MembershipPersonStartContext': {
                'value': 'Born',
                'sources': access_points,
                'confidence': '1',
            },
            'MembershipPerson_MembershipPersonEndContext': {
                'value': 'Died',
                'sources': access_points,
                'confidence': '1',
            },
            'MembershipPerson_MembershipPersonFirstCitedDate': {
                'value': '2002-01-01',
                'sources': access_points,
                'confidence': '1',
            },
            'MembershipPerson_MembershipPersonLastCitedDate': {
                'value': '2003-01-01',
                'sources': access_points,
                'confidence': '1',
            },
        }

        memberships.append(MembershipPerson.create(mem_info))

    return memberships


@pytest.fixture
def violation(access_points,
              people,
              organizations,
              location_node,
              location_adminlevel1,
              location_adminlevel2):

    # # Descriptions and other attributes
    # self.perpetratorclassification = ComplexFieldContainer(
    #     self, ViolationPerpetratorClassification
    # )
    # self.types = ComplexFieldListContainer(self, ViolationType)

    violation_info = {
        'Violation_ViolationStartDate': {
            'value': '2003-08-09',
            'sources': access_points,
            'confidence': '2',
        },
        'Violation_ViolationEndDate': {
            'value': '2003-08-10',
            'sources': access_points,
            'confidence': '2',
        },
        'Violation_ViolationLocationDescription': {
            'value': 'Out back',
            'sources': access_points,
            'confidence': '2',
        },
        'Violation_ViolationAdminLevel1': {
            'value': location_adminlevel1,
            'sources': access_points,
            'confidence': '2',
        },
        'Violation_ViolationAdminLevel2': {
            'value': location_adminlevel2,
            'sources': access_points,
            'confidence': '2',
        },
        'Violation_ViolationDivisionId': {
            'value': 'ocd-division/country:us',
            'sources': access_points,
            'confidence': '2',
        },
        'Violation_ViolationLocation': {
            'value': location_node,
            'sources': access_points,
            'confidence': '2',
        },
        'Violation_ViolationDescription': {
            'value': 'something real bad',
            'sources': access_points,
            'confidence': '2',
        },
        'Violation_ViolationPerpetrator': {
            'value': people[0],
            'sources': access_points,
            'confidence': '2',
        },
        'Violation_ViolationPerpetratorOrganization': {
            'value': organizations[0],
            'sources': access_points,
            'confidence': '2',
        },
        'Violation_ViolationType': {
            'value': 'Violations against humanity',
            'sources': access_points,
            'confidence': '2',
        },
    }

    return Violation.create(violation_info)

@pytest.fixture
def fake_signal(mocker):
    fake_signal = mocker.patch('complex_fields.base_models.object_ref_saved.send')
    return fake_signal
