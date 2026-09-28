from app.config import Settings
from app.core.clock import Clock
from app.domain.player import Player

from datetime import datetime, timezone
# a = Settings()
# # print(a)

p = Player(1, "Bob")
print(p.id)
print(p.nickname)
print(p.created_at)
print()
dto = p.to_dto()
print(dto.id)
print(dto.nickname)
print()
data = p.to_dict()
print(data)
print(type(data["created_at"]))

print("mmmmmmmmmmmmm")
data = p.to_dict()
p2 = Player.from_dict(data)

print(p2.id)
print(p2.nickname)
print(p2.created_at)
# clock = Clock()
# print(clock.speed)
# print(clock.now())
# print(datetime.now(timezone.utc))
# print(clock.elapsed_sec(datetime.fromisoformat("2026-09-27 19:29:45.557875+00:00"),datetime.now(timezone.utc)))
# #print(clock.elapsed_sec(2026-09-27 19:29:45.557875+00:00))