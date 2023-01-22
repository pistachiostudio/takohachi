from .repository import TriggerRepository


def get_trigger_repository() -> TriggerRepository:
    return TriggerRepository()

