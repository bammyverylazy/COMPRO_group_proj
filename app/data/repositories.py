class PlayerRepository(BaseRepository):
    def key_of(item: Player):
        return item.id

    def item_from_dict(data: dict[str, Any]):
        return ....


class SpeciesRepository(BaseRepository):
    def key_of(item: Player):
        return item.id

    def item_from_dict(data: dict[str, Any]):
        return Player.from_dict

    def find_by_nickname(nickname: str):


class SessionRepository(BaseRepository):
    def
