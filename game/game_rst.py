from flask import session
from flask_restx import Resource
from flask_fullstack import ResourceController
from flask_restx.reqparse import RequestParser

from . import Shapes, GameActPerUser, Game
from common import User


controller = ResourceController(name="game", path="/game/")


game_parser = RequestParser()
game_parser.add_argument("game_id", type=int, required=True)
game_parser.add_argument("user_id", type=int, required=True)


@controller.route("/shapes/")
class Shape(Resource):

    @controller.jwt_authorizer(User)
    def get(self):
        return Shapes.list()


@controller.route("/results/")
class GameResults(Resource):

    @controller.jwt_authorizer(User)
    @controller.argument_parser(game_parser)
    @controller.marshal_with(GameActPerUser.ResultModel)
    def get(self, game_id: int, user_id: int):
        game = GameActPerUser.find_by_game_and_user_ids(
            game_id=game_id,
            user_id=user_id
        )
        return game.result


@controller.route("/all/")
class Games(Resource):

    @controller.jwt_authorizer(User)
    @controller.marshal_with(Game.MainData)
    def get(self, user: User):
        return Game.get_all(user_id=user.id)


@controller.route("/all-detailed/")
class GamesDetailed(Resource):

    @controller.jwt_authorizer(User)
    @controller.marshal_with(GameActPerUser.MainData)
    def get(self, user: User):
        return GameActPerUser.get_all(user_id=user.id)
