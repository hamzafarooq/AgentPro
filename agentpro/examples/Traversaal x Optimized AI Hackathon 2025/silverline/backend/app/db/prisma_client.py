import prisma
import asyncio
from datetime import timedelta
from app.utils.logging.logger import LOG


prisma_client = prisma.Prisma(auto_register=True)
connection_timeout = 10  # Reduced timeout to fail faster


async def connect_prisma():
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            await prisma_client.connect(timeout=timedelta(seconds=connection_timeout))
            LOG.info("Successfully connected to Prisma.")
            # Test connection with a simple query
            try:
                # Simple query to test if the connection actually works
                await prisma_client.callhistory.count()
                LOG.info("Database connection verified - successful query execution.")
            except Exception as e:
                LOG.error(f"Database connection test failed: {str(e)}")
                # Continue anyway, as we'll use fallback data
            break
        except Exception as e:
            LOG.error(f"Failed to connect to Prisma (Attempt {attempt}/{max_retries}): {str(e)}")
            if attempt < max_retries:
                await asyncio.sleep(3)
    else:
        LOG.error("Unable to connect to Prisma after multiple attempts.")
        # Don't raise exception here, let the app continue with fallback data
        LOG.warning("Application will run with fallback data due to database connection issues.")


async def disconnect_prisma():
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            await prisma_client.disconnect(timeout=timedelta(seconds=connection_timeout))
            LOG.info("Successfully disconnected from Prisma")
            break
        except Exception as e:
            LOG.error(f"Failed to disconnect from Prisma (Attempt {attempt}/{max_retries}): {str(e)}")
            if attempt < max_retries:
                await asyncio.sleep(3)
    else:
        LOG.error("Unable to disconnect from Prisma after multiple attempts.")
        # No need to raise an exception on disconnect failure

    