from datetime import datetime, timezone
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from service.controllers.request_access_token_controller import \
    generate_afip_access_token
from service.time.time_management import \
    generate_ntp_timestamp as time_provider
from service.utils.logger import logger
from service.xml_management.xml_builder import is_expired, xml_exists

scheduler = AsyncIOScheduler()

async def run_job():
    logger.info("Starting job: verifying token expiration for all tenants")

    certs_dir = Path("service/app_certs")
    if not certs_dir.exists():
        logger.info("No app_certs directory found, skipping scheduler run.")
        return

    for cuit_dir in certs_dir.iterdir():
        if not cuit_dir.is_dir():
            continue
        cuit = cuit_dir.name
        try:
            if not xml_exists("loginTicketRequest.xml", cuit):
                await generate_afip_access_token(cuit)
                continue

            if xml_exists("loginTicketResponse.xml", cuit):
                if is_expired("loginTicketResponse.xml", time_provider, cuit):
                    await generate_afip_access_token(cuit)
                else:
                    logger.info(f"Token not expired for CUIT {cuit}.")
                continue

            if not xml_exists("loginTicketResponse.xml", cuit):
                await generate_afip_access_token(cuit)

        except Exception as e:
            logger.error(f"Error renewing token for CUIT {cuit}: {e}")

    logger.info("Scheduler job finished for all tenants.")


def start_scheduler():
    logger.info("Scheduler starting: job configured to run every 11 hours")

    scheduler.add_job(
        run_job,
        trigger="interval",
        hours=11,
        id="afip_token_watchdog",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        next_run_time=datetime.now(timezone.utc)
    )
    scheduler.start()

def stop_scheduler():
    scheduler.shutdown(wait=False)
