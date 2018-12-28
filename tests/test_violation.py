import pytest

from django.test import TestCase, Client
from django.core.urlresolvers import reverse_lazy
from django.db import connection
from django.core.management import call_command
from django.contrib.auth.models import User

from source.models import AccessPoint
from person.models import Person
from organization.models import Organization
from violation.models import Violation, ViolationType, \
    ViolationPerpetratorClassification


@pytest.mark.django_db
def test_view_violation(client, violation):

    response = client.get(reverse_lazy('view-violation', args=[violation.uuid]))

    assert response.status_code == 200


@pytest.mark.django_db
def test_edit_violation(setUp,
                        violation,
                        new_access_points,
                        new_people,
                        new_organizations,
                        fake_signal):

    new_types = ['Violation against freedom from torture']

    perpetrators = [p.id for p in new_people]
    perpetratororganizations = [o.id for o in new_organizations]
    perpetratorclassification = 'Real bad guys'

    response = setUp.get(reverse_lazy('edit-violation', kwargs={'slug': violation.uuid}))

    assert response.status_code == 200

    new_source_ids = [s.uuid for s in new_access_points]

    post_data = {
        'division_id': 'ocd-division/country:us',
        'division_id_source': new_source_ids,
        'startdate': '1976',
        'startdate_source': new_source_ids,
        'enddate': '2012-02-14',
        'enddate_source': new_source_ids,
        'types': new_types,
        'types_source': new_source_ids,
        'perpetrator': perpetrators,
        'perpetrator_source': new_source_ids,
        'perpetratororganization': perpetratororganizations,
        'perpetratororganization_source': new_source_ids,
        'perpetratorclassification': perpetratorclassification,
        'perpetratorclassification_source': new_source_ids,
        'description': violation.description.get_value().value,
        'description_source': new_source_ids,
    }

    response = setUp.post(reverse_lazy('edit-violation', kwargs={'slug': violation.uuid}), post_data)

    assert response.status_code == 302

    assert set(new_source_ids) <= {s.uuid for s in violation.description.get_sources()}

    assert violation.division_id.get_value().value == 'ocd-division/country:us'
    assert str(violation.startdate.get_value().value) == '1976'
    assert str(violation.enddate.get_value().value) == '14th February 2012'
    assert new_types[0] in [v.get_value().value for v in violation.types.get_list()]
    assert violation.perpetratorclassification.get_value().value == perpetratorclassification

    for person in new_people:
        assert person in [p.get_value().value for p in violation.perpetrator.get_list()]

    fake_signal.assert_called_with(object_id=violation.uuid, sender=Violation)
