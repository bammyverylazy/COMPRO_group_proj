from datetime import datetime

from app.domain.egg_factory import EggFactory
from app.domain.gacha import GachaMachine
from app.domain.owned_pet import OwnedPet
from app.domain.pet_policy import PetLevelPolicy
from app.domain.species import Species
from app.domain.tier_odds_table import TierOddsTable
from app.dto import HatchResult
from app.errors import InvalidStateError

class HatchService:
    def __init__(self, store):
        self.store = store
        self.factory = EggFactory()
        self.odds_table = TierOddsTable()
        self.gacha = GachaMachine()
        self.policy = PetLevelPolicy()
        
    def roll_tier(self, duration_sec: int):
        odds = self.odds_table.odds_for(duration_sec)

        if not odds:
            raise InvalidStateError("Study session is too short to hatch")

        return self.gacha.pick_tier(odds)
    
    def hatch(self, session_id: int, tier=None):
        session = self.store.sessions.get(session_id)

        if not session.can_hatch():
            raise InvalidStateError("Session is not ready to hatch")
        
        if tier is None:
            tier = self.roll_tier(session.duration_sec)
            
        egg = self.factory.create(tier)
        pool = self.store.species.list_by_tier(tier)
        species = egg.roll_species(pool, self.gacha)
        pet, is_new = self._give_pet(session.player_id, species)

        session.mark_hatched(tier, species.code)

        self.store.save()

        return HatchResult(
            session_id=session.id,
            player_id=session.player_id,
            tier=tier,
            pet=pet.to_dto(species, self.policy),
            is_new=is_new,
        )
        
    def _give_pet(self, player_id: int, species: Species):
        existing = self.store.pets.find_owned(
            player_id,
            species.code,
        )

        if existing is not None:
            existing.level_up(self.policy)
            return existing, False

        pet = OwnedPet(
            player_id=player_id,
            species_code=species.code,
            hatched_at=datetime.now(),
        )
        self.store.pets.add(pet)
        return pet, True