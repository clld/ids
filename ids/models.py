from zope.interface import implementer
from sqlalchemy import (
    Column,
    String,
    Unicode,
    Integer,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin
from clld.db.models.common import (
    Parameter, IdNameDescriptionMixin, Contribution, Language,
)


class Chapter(Base, IdNameDescriptionMixin):
    pass


#-----------------------------------------------------------------------------
# specialized common mapper classes
#-----------------------------------------------------------------------------
@implementer(interfaces.IParameter)
class Entry(Parameter, CustomModelMixin):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)
    chapter_pk = Column(Integer, ForeignKey('chapter.pk'), nullable=False)
    chapter = relationship(Chapter, backref='entries')
    sub_code = Column(String)

    french = Column(Unicode)
    russian = Column(Unicode)
    spanish = Column(Unicode)
    portugese = Column(Unicode)


@implementer(interfaces.IContribution)
class Dictionary(Contribution, CustomModelMixin):
    pk = Column(Integer, ForeignKey('contribution.pk'), primary_key=True)
    language_pk = Column(Integer, ForeignKey('language.pk'), nullable=False)
    language = relationship(Language, backref=backref('dictionary', uselist=False))
