from flask_fullstack import EventController, EventSpace, DuplexEvent
from flask_socketio import join_room, leave_room

from common import User
from . import Game, GameActPerUser


controller = EventController()


@controller.route()
class RoomEventSpace(EventSpace):

    @controller.jwt_authorizer(User)
    @controller.argument_parser(User.MainData)
    @controller.mark_duplex(Game.MainData, use_event=True)
    @controller.marshal_ack(Game.MainData)
    def start(self, event: DuplexEvent, user: User) -> str:
        game = Game.create()
        join_room(game.room_code)
        event.emit_convert(
            game,
            data={'room_code': game.room_code},
            room=game.room_code,
            include_self=True)

    @controller.jwt_authorizer(User)
    @controller.argument_parser(User.MainData)
    def join(self, user: User, room_code: str):
        join_room(room_code)

    @controller.jwt_authorizer(User)
    @controller.argument_parser(User.MainData)
    def leave(self, user: User, room_code: str):
        leave_room(room_code)

    def get_results(
        self,
        game_id: int,
        user_id: int,
        user_shape: str,
        enemy_id: int,
        enemy_shape: str
    ):
        game_user = GameActPerUser.find_by_game_and_user_ids(game_id, user_id)
        game_enemy = GameActPerUser.find_by_game_and_user_ids(game_id, enemy_id)

        if user_shape == enemy_shape:
            game_user.result, game_enemy.result = 'TIE', 'TIE'
        elif (
            user_shape.lower() == 'scissors' and enemy_shape.lower() == 'rock'
        ) or (
            user_shape.lower() == 'paper' and enemy_shape.lower() == 'scissors'
        ) or (user_shape.lower() == 'rock' and enemy_shape.lower() == 'paper'):
            game_user.result, game_enemy.result = 'LOSE', 'WIN'
        else:
            game_user.result, game_enemy.result = 'WIN', 'LOSE'

    @controller.jwt_authorizer(User)
    @controller.argument_parser()
    @controller.mark_duplex(GameActPerUser.MainData, use_event=True)
    @controller.marshal_ack(GameActPerUser.MainData)
    def make_shape_choice(
        self,
        event: DuplexEvent,
        game_id: int,
        room_code: str,
        user: User,
        shape: str
    ):
        game = GameActPerUser.find_by_game_and_user_ids(game_id, user.id)
        game.shape = shape
        enemy = GameActPerUser.get_enemy(game_id, user.id)
        enemys_shape = enemy.shape
        if enemys_shape:
            self.get_results(game_id, user.id, shape, enemy.id, enemys_shape)
            return event.emit_convert(
                game,
                room=room_code,
                include_self=True
            )
