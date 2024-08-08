import re
from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", cls.__name__).lower()

    # add a method so that we can extract it as dict
    def to_dict(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
