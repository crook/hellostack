# -*- coding: utf-8 -*-

import logging
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from hellostack.exceptions import *

log = logging.getLogger(__name__)

engine = create_engine('sqlite:///./flavor.db', echo=True)
Base = declarative_base()

class Flavor(Base):
    """Flavor object to sepcify VM profile"""

    __tablename__ = "falvors"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    vcpu = Column(Integer)
    ram = Column(Integer)
    disk = Column(Integer)

    def __repr__(self):
        return "<Flavor(name=%s, id=%d)>" %(self.name, self.id)


def init_db():

    Base.metadata.create_all(engine)


def get_session():

    init_db()

    _session = sessionmaker(bind=engine)

    # invoke __call__ method
    if _session is None:
        raise InvalidSession("Session is None, call init_db first")

    return _session()

if __name__ == "__main__":
    pass
