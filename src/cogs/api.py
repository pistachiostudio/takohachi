from settings import CLIENT_SECRETS_PATH

from .repository import TriggerRepository


def get_trigger_repository() -> TriggerRepository:
    return TriggerRepository(CLIENT_SECRETS_PATH)
