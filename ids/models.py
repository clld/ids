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
    Parameter, IdNameDescriptionMixin, Contribution, Language, Value, Unit, ValueSet,
)
from clld.web.util import concepticon
from clld_glottologfamily_plugin.models import HasFamilyMixin

from ids.interfaces import IChapter


ROLES = {
    # tuples of ('human readable header', 'column header in languages.csv')
    2: ('Author', 'Authors'),
    3: ('Consultant', 'Consultants'),
    1: ('Data Entry', 'DataEntry'),
}


@implementer(IChapter)
class Chapter(Base, IdNameDescriptionMixin):
    count_entries = Column(Integer)


@implementer(interfaces.IParameter)
class Entry(CustomModelMixin, Parameter):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)
    chapter_pk = Column(Integer, ForeignKey('chapter.pk'), nullable=False)
    chapter = relationship(Chapter, backref='entries')
    sub_code = Column(String)
    concepticon_id = Column(Integer)
    concepticon_gloss = Column(Unicode)
    concepticon_concept_id = Column(Unicode)
    representation = Column(Integer)

    french = Column(Unicode)
    russian = Column(Unicode)
    spanish = Column(Unicode)
    portuguese = Column(Unicode)

    def concepticon_link(self, req):
        return concepticon.link(
            req,
            id=self.concepticon_concept_id,
            label=self.concepticon_gloss or self.concepticon_concept_id,
            obj_type='Concept')


@implementer(interfaces.ILanguage)
class IdsLanguage(CustomModelMixin, Language, HasFamilyMixin):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)


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

    org_value = Column(Unicode)
    comment = Column(Unicode)


@implementer(interfaces.IValueSet)
class Synset(CustomModelMixin, ValueSet):
    """a synset is the set of all counterparts for one meaning in one dictionary.
    """
    pk = Column(Integer, ForeignKey('valueset.pk'), primary_key=True)

    alt_representation = Column(Unicode)
