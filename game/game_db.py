from __future__ import annotations
import string
import random

from flask_fullstack import TypeEnum, PydanticModel

from sqlalchemy import Column, ForeignKey, select
from sqlalchemy.types import Integer, String, Enum
from sqlalchemy.orm import relationship

from common import Base, db, User


class ShapeChoices(TypeEnum):
    ROCK = 0
    PAPER = 1
    SCISSORS = 2


class GameResults(TypeEnum):
    WIN = 0
    LOSE = 1
    TIE = 2


class Game(Base):
    __tablename__ = "games"

    id: Column | int = Column(Integer, primary_key=True)
    room_code: Column | str = Column(
        String(10),
        unique=True,
        nullable=False
    )

    MainData = PydanticModel.column_model(id, room_code)

    @staticmethod
    def generate_room_code() -> str | None:
        characters = string.ascii_lowercase + string.digits
        return ''.join(random.choices(characters, k=10))

    @classmethod
    def create(cls, id: int = None) -> Game | None:
        room_code = cls.generate_room_code()
        return super().create(room_code=room_code, id=id)

    @classmethod
    def find_by_id(cls, id: int) -> Game | None:
        return db.get_first(select(cls).filter_by(id=id))

    @classmethod
    def find_by_room_code(cls, room_code: str) -> Game | None:
        return db.get_first(select(cls).filter_by(room_code=room_code))


class GameActPerUser(Base):
    __tablename__ = "gameacts"

    id: Column | int = Column(Integer, primary_key=True)
    game_id: Column | int = Column(
        Integer,
        ForeignKey("games.id"),
        nullable=False
    )
    game: relationship = relationship(Game)
    user_id: Column | int = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )
    user: relationship = relationship(User)
    shape: Column | Enum = Column(Enum(ShapeChoices))
    result: Column | Enum = Column(Enum(GameResults))

    MainData = PydanticModel.column_model(id, game_id, user_id, shape, result)

    @classmethod
    def create(
        cls,
        game_id: int,
        user_id: int,
        shape: str = None,
        result: str = None
    ) -> GameActPerUser | None:
        return super().create(
            game_id=game_id,
            user_id=user_id,
            shape=shape,
            result=result)

    @classmethod
    def find_by_game_and_user_ids(
        cls,
        game_id: int,
        user_id: int
    ) -> GameActPerUser | None:
        return db.get_first(select(cls).filter_by(
            game_id=game_id,
            user_id=user_id))

    @classmethod
    def find_enemy(cls, game_id: int, user_id: int) -> GameActPerUser | None:
        return db.get_first(select(cls).where(
            game_id == game_id,
            user_id != user_id))
