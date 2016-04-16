# coding: utf-8
from sqlalchemy import Column, Date, DateTime, Float, Index, Integer, SmallInteger, String, \
    BigInteger, Boolean, ForeignKey, Text, Enum, Table
from sqlalchemy.ext.declarative import declarative_base,declared_attr
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class Base(db.Model):
    __abstract__=True

    id =  Column(BigInteger, primary_key=True)
    
    def __repr__(self, attrs=None):
        base= '<%s id=%s' % (self.__class__.__name__, self.id)
        if attrs:
            base+=' '+' '.join(['%s="%s"'%(a, getattr(self,a)) for a in attrs])
        return base +'>'

#Base = declarative_base(cls=Base)

ebook_genres = Table('ebook_genres', Base.metadata,
                      Column('ebook_id', ForeignKey('ebook.id'), primary_key=True, index=True),
                      Column('genre_id', ForeignKey('genre.id'), primary_key=True, index=True))

ebook_authors = Table('ebook_authors', Base.metadata, 
                      Column('ebook_id', ForeignKey('ebook.id'), primary_key=True, index=True),
                      Column('author_id', ForeignKey('author.id'), primary_key=True, index=True))

user_roles = Table('user_roles', Base.metadata, 
                      Column('user_id', ForeignKey('user.id'), primary_key=True, index=True),
                      Column('role_id', ForeignKey('role.id'), primary_key=True, index=True))

# series_authors = Table('series_authors', Base.metadata, 
#                       Column('series_id', ForeignKey('series.id'), primary_key=True),
#                       Column('author_id', ForeignKey('author.id'), primary_key=True))


class Auditable(object):
    created = Column(DateTime, nullable=False, default=func.now())
    modified = Column(DateTime, nullable=False,index=True)
    
    @declared_attr
    def created_by_id(cls):  # @NoSelf
        return Column(BigInteger, ForeignKey('user.id'))
    
    @declared_attr
    def created_by(cls):  # @NoSelf\
        return relationship('User', primaryjoin="User.id==%s.created_by_id" % cls.__name__)
    
    @declared_attr
    def modified_by_id(cls):  # @NoSelf
        return Column(BigInteger, ForeignKey('user.id'))
    
    @declared_attr
    def modified_by(cls):  # @NoSelf\
        return relationship('User', primaryjoin="User.id==%s.modified_by_id" % cls.__name__)
    
class User(Base, Auditable):
    user_name= Column(String(128), nullable=False)
    email= Column(String(128), nullable=False)
    password = Column(String(128), nullable=False)
    roles=relationship('Role', secondary=user_roles)
    
class Role(Base):
    name=Column(String(64), nullable=False)
    
    def __repr__(self):
        return super(Role,self).__repr__(['name'])
    
class Author(Base, Auditable):
    
    last_name = Column(String(128), nullable=False)
    first_name = Column(String(128), nullable=True)
    description = Column(Text)
    
    def __repr__(self):
        return super(Author,self).__repr__(['first_name', 'last_name'])


class Bookshelf(Base, Auditable):
    name = Column(String(256), nullable=False, index=True)
    description = Column(String)
    public = Column(Boolean, default=True)
    rating = Column(Float(asdecimal=True))
    items=relationship('BookshelfItem', back_populates='bookshelf')
    
    def __repr__(self):
        return super(Bookshelf,self).__repr__(['name'])


class BookshelfItem(Base, Auditable):
    
    type = Column(Enum('EBOOK', 'SERIES', name='BOOKSHELF_ITEM_TYPE'), nullable=False)
    bookshelf_id = Column(BigInteger, ForeignKey('bookshelf.id'), nullable=False)
    ebook_id = Column(BigInteger, ForeignKey('ebook.id'))
    ebook= relationship('Ebook')
    series_id = Column(BigInteger, ForeignKey('series.id'))
    series=relationship('Series')
    order = Column(Integer)
    note = Column(Text)
    bookshelf=relationship('Bookshelf', back_populates='items')
    
    def __repr__(self):
        return super(BookshelfItem,self).__repr__(['type'])


class Conversion(Base, Auditable):
    
    batch_id = Column(BigInteger, ForeignKey('conversion_batch.id'))
    source_id = Column(BigInteger, ForeignKey('source.id'), nullable=False)
    source=relationship('Source')
    location = Column(String(512), nullable=False)
    format_id = Column(BigInteger, ForeignKey('format.id'), nullable=False)
    format=relationship('Format', lazy='joined', innerjoin=True)
    batch=relationship('ConversionBatch', back_populates='items')


class ConversionBatch(Base, Auditable):
    
    name = Column(String(100), nullable=False)
    for_entity = Column(Enum('SERIES','AUTHOR', 'EBOOK', 'SOURCE', name='CONVERSION_BATCH_ENTITY'))
    entity_id = Column(BigInteger)
    format_id = Column(BigInteger, ForeignKey('format.id'), nullable=False)
    items=relationship('Conversion', back_populates='batch')



class Ebook(Base, Auditable):
    title = Column(String(256), nullable=False, index=True)
    description = Column(Text)
    language_id = Column(BigInteger, ForeignKey('language.id'), nullable=False)
    language = relationship('Language', lazy='joined', innerjoin=True)
    series_id = Column(BigInteger, ForeignKey('series.id'), index=True)
    series=relationship('Series', back_populates='books', lazy='joined')
    series_index = Column(Integer)
    rating = Column(Float(asdecimal=True))
    sources = relationship('Source', back_populates='ebook')
    genres = relationship('Genre', secondary=ebook_genres)
    authors= relationship('Author', secondary=ebook_authors, order_by='Author.id', lazy='subquery')
    cover= Column(String(512))
    
    def __repr__(self):
        return super(Ebook,self).__repr__(['title'])



class Format(Base):
    mime_type = Column(String(128), nullable=False)
    name = Column(String(64), nullable=False)
    extension = Column(String(8), nullable=False, unique=True)
    
    def __repr__(self):
        return super(Format,self).__repr__(['extension', 'mime_type', 'name'])


class Language(Base):
    code = Column(String(6), nullable=False, unique=True)
    name = Column(String(64), nullable=False)
    
    def __repr__(self):
        return super(Language,self).__repr__(['name', 'code'])


class Series(Base, Auditable):
    title = Column(String(256), nullable=False, index=True)
    rating = Column(Float(asdecimal=True))
    description = Column(Text)
    books=relationship('Ebook', back_populates='series', lazy='dynamic')
    
    #authors= relationship('Author', secondary=ebook_authors, order_by='author.id', lazy='subquery')
    
    def __repr__(self):
        return super(Series,self).__repr__(['title'])


class Source(Base, Auditable):
    ebook_id = Column(BigInteger, ForeignKey('ebook.id'), nullable=False)
    ebook= relationship('Ebook', back_populates='sources')
    location = Column(String(512), nullable=False)
    load_source = Column(String(256))
    format_id = Column(BigInteger, ForeignKey('format.id'), nullable=False)
    format=relationship('Format', lazy='joined', innerjoin=True)
    size = Column(Integer, nullable=False)
    hash = Column(String(128), nullable=False)
    quality = Column(Float(asdecimal=True))
    
    def __repr__(self):
        return super(Source,self).__repr__(['location'])
    
class Genre(Base):
    name = Column(String(64), nullable=False, unique=True)
    
    def __repr__(self):
        return super(Genre,self).__repr__(['name'])
    
    
    
    