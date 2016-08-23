# pylint: disable=no-init, old-style-class
"""Provides implementation of UserFactory"""

from base_factory import BaseFactory
from model import User
from factory.fuzzy import FuzzyText, FuzzyChoice
import factory
import util


class UserFactory(BaseFactory):
    """Factory for creating mock users"""
    class Meta: # pylint: disable=missing-docstring
        model = User

    name     = FuzzyChoice(['John Doe', 'Machete', 'Bobby Tables'])
    username = factory.Sequence(lambda n: 'bobby%d' % n)
    email_p    = factory.LazyAttribute(lambda user: '%s@example.com' % user.username)
    verified_p = FuzzyChoice([True, False])
    active_p   = FuzzyChoice([True, False])
    bio      = FuzzyChoice(['All component things\'', 'are impermanent.',' work out your',' own salvation ','with diligence.'])
    facebook = FuzzyText()
    twitter  = FuzzyText()
    gplus    = FuzzyText()
    instagram= FuzzyText()
    linkedin = FuzzyText()
    github   = FuzzyText()

    @classmethod
    def create_batch(cls, size, **kwargs):
        """When creating batch, we create one less than requested size and then add admin user
        at the end"""
        super(UserFactory, cls).create_batch(size - 1, **kwargs)
        cls.create_admin()

    @classmethod
    def create_admin(cls):
        """Creates mock admin user"""
        cls ( username='admin'
            , pwdhash_h=util.password_hash('123456')
            , admin_p=True
            , verified_p=True
            , active_p=True
            )
