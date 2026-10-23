import logging
from json import JSONDecodeError
import httpx
from socmedAPI.config import config
from databases import Database
from socmedAPI.database import post_table, database

logger = logging.getLogger(__name__)

class APIResponseError(Exception):
    pass


async def _generate_cute_creature_api(prompt: str):
    logger.debug("Generating cute creature")
    async with httpx.AsyncClient() as client:
        try:
            response =  await client.post(
                "https://api.deepai.org/api/text2img",
                data={"text": prompt},
                headers={"api-key": config.DEEPAI_API_KEY},
                timeout=60
            )
            logger.debug(response)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as err:
            raise APIResponseError(
                f"API request failed with status code {err.response.status_code}"
            ) from err
        except (JSONDecodeError, TypeError) as err:
            raise APIResponseError("API response parsing failed") from err



async def generate_and_add_to_post(
    email: str,
    post_id: int,
    post_url: str,
    database: Database,
    prompt: str = "A black british shorthair with golden eyes laying on the ground",
):
    try: 
        response = await _generate_cute_creature_api(prompt)
    except APIResponseError:
        return "Oops, failed ToT...."
    

    logger.debug("Connecting to database to update post")

    query = (
        post_table.update()
        .where(post_table.c.id == post_id)
        .values(image_url=response["output_url"])
    )

    logger.debug(query)

    await database.execute(query)

    logger.debug("Database connection in background task closed")

    return response