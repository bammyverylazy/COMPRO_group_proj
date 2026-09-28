from app.config import Settings
from app.core.clock import Clock
from datetime import datetime, timezone
a = Settings()
print(a)


clock = Clock()
print(clock.speed)
print(clock.now())
print(datetime.now(timezone.utc))
print(clock.elapsed_sec(datetime.fromisoformat("2026-09-27 19:29:45.557875+00:00"),datetime.now(timezone.utc)))
#print(clock.elapsed_sec(2026-09-27 19:29:45.557875+00:00))