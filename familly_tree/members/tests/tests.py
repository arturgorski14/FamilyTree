from django.contrib.auth.models import User
from django.test import TestCase  # noqa E501


# Create your tests here.
def test_example():
    assert 1 == 0, "failed as expected"


def test_example_passing():
    assert 1 == 1, "passed"


# def test_create_user():
#     User.objects.create_user('test', 'test@test.com', 'pass')
#     assert User.objects.count() == 1
