from __future__ import annotations
import string
import random

from flask_fullstack import TypeEnum, PydanticModel
from sqlalchemy import Column, ForeignKey, select
from sqlalchemy.types import Integer, String, Enum
from sqlalchemy.orm import relationship

from common import Base, db, User


class Shapes(TypeEnum):
    ROCK = "ROCK"
    PAPER = "PAPER"
    SCISSORS = "SCISSORS"

    @classmethod
    def list(cls) -> list:
        return [shape.value for shape in Shapes]


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
    def create(cls, game_id: int = None) -> Game | None:
        room_code = cls.generate_room_code()
        return super().create(room_code=room_code, game_id=id)

    @classmethod
    def find_by_id(cls, game_id: int) -> Game | None:
        return db.get_first(select(cls).filter_by(game_id=id))

    @classmethod
    def find_by_room_code(cls, room_code: str) -> Game | None:
        return db.get_first(select(cls).filter_by(room_code=room_code))

    @classmethod
    def get_all(cls, user_id: int) -> list | None:
        return db.session.query(cls).filter_by(user_id=user_id).all()


class GameActPerUser(Base):
    __tablename__ = "gameacts"

    id: Column | int = Column(Integer, primary_key=True)
    game_id: Column | int = Column(
        Integer,
        ForeignKey("games.id"),
        nullable=False
    )
    user_id: Column | int = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )
    shape: Column | Shapes = Column(Enum(Shapes))
    result: Column | GameResults = Column(Enum(GameResults))

    game: relationship = relationship(Game)
    user: relationship = relationship(User)

    MainData = PydanticModel.column_model(id, game_id, user_id, shape, result)
    ShapeModel = PydanticModel.column_model(shape)
    ResultModel = PydanticModel.column_model(result)

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

    @classmethod
    def get_all(cls, user_id: int) -> list | None:
        return db.session.query(cls).filter_by(user_id=user_id).all()
