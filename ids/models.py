from collections import OrderedDict

from zope.interface import implementer
from sqlalchemy import (
    Column,
    String,
    Unicode,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import relationship, backref

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin
from clld.db.models.common import (
    Parameter, IdNameDescriptionMixin, Contribution, Language, Value, Unit,
)


ROLES = OrderedDict()
ROLES[2] = 'Author'
ROLES[3] = 'Consultant'
ROLES[1] = 'Data Entry'


class Chapter(Base, IdNameDescriptionMixin):
    pass


#-----------------------------------------------------------------------------
# specialized common mapper classes
#-----------------------------------------------------------------------------
@implementer(interfaces.IParameter)
class Entry(CustomModelMixin, Parameter):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)
    chapter_pk = Column(Integer, ForeignKey('chapter.pk'), nullable=False)
    chapter = relationship(Chapter, backref='entries')
    sub_code = Column(String)

    french = Column(Unicode)
    russian = Column(Unicode)
    spanish = Column(Unicode)
    portugese = Column(Unicode)


@implementer(interfaces.IContribution)
class Dictionary(CustomModelMixin, Contribution):
    pk = Column(Integer, ForeignKey('contribution.pk'), primary_key=True)
    language_pk = Column(Integer, ForeignKey('language.pk'), nullable=False)
    language = relationship(Language, backref=backref('dictionary', uselist=False))

    default_representation = Column(Unicode)
    alt_representation = Column(Unicode)


@implementer(interfaces.IUnit)
class Word(CustomModelMixin, Unit):
    pk = Column(Integer, ForeignKey('unit.pk'), primary_key=True)

    alt_name = Column(Unicode)
    alt_description = Column(Unicode)


@implementer(interfaces.IValue)
class Counterpart(CustomModelMixin, Value):
    """a counterpart relates a meaning with a word
    """
    pk = Column(Integer, ForeignKey('value.pk'), primary_key=True)

    word_pk = Column(Integer, ForeignKey('unit.pk'))
    word = relationship(Word, backref='counterparts')
