from settings import ADD_SSL_CLIENT_SECRETS_PATH

from .repository import TriggerRepository


def get_trigger_repository() -> TriggerRepository:
    return TriggerRepository(ADD_SSL_CLIENT_SECRETS_PATH)
