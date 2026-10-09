import logging

from socmedAPI.database import database, user_table

logger = logging.getLogger(__name__)

async def get_user(email: str):
    logger.debug(f"Fetching user with email: {email}")
    result = user_table.select().where(user_table.c.email == email)
    
    return await database.fetch_one(result)
    if result:
        return result
    else:
        logger.warning(f"No user found with email: {email}")
        return None