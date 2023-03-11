from .repository import TriggerRepository
from settings import ADD_SSL_CLIENT_SECRETS_PATH 


def get_trigger_repository() -> TriggerRepository:
    return TriggerRepository(ADD_SSL_CLIENT_SECRETS_PATH)
