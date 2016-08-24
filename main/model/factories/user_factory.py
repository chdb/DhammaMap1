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

    name     = FuzzyChoice(['Gloria Bloggs', 'Ebenezer Dingbat', 'Algernon Usher'])
    username = factory.Sequence(lambda n: 'tutshka%d' % n)
    email_    = factory.LazyAttribute(lambda user: '%s@example.com' % user.username)
    isVerified_ = FuzzyChoice([True, False])
    isActive_   = FuzzyChoice([True, False])
    bio      = FuzzyChoice(['All component things\'', 'are impermanent.',' work out your',' own salvation ','with diligence.'])
    facebook = FuzzyText()
    twitter  = FuzzyText()
    gplus    = FuzzyText()
    instagram= FuzzyText()
    linkedin = FuzzyText()
    github   = FuzzyText()
    pwdhash__=util.password_hash('654321')

    @classmethod
    def create_batch(cls, size, **kwargs):
        """When creating a batch, we create one less than requested and add admin user at the end"""
        super(UserFactory, cls).create_batch(size - 1, **kwargs)
        cls.create_admin()

    @classmethod
    def create_admin(cls):
        """Creates mock admin user"""
        cls ( username='admin'
            , pwdhash__=util.password_hash('123456')
            , isAdmin_=True
            , isVerified_=True
            , isActive_=True
            )
