"""
Celery tasks for birlikteyiz app
"""
from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.management import call_command
from django.utils import timezone
from .models import CronJob

logger = get_task_logger(__name__)


@shared_task(name='birlikteyiz.fetch_earthquakes')
def fetch_earthquakes_task():
    """
    Periodic task to fetch earthquake data from all sources
    Runs every 5 minutes
    """
    logger.info("Starting earthquake data fetch task")

    try:
        # Update CronJob status
        cron_job = CronJob.objects.get(name='Fetch Earthquakes')
        cron_job.status = 'running'
        cron_job.last_run = timezone.now()
        cron_job.save()

        # Execute the management command
        call_command('fetch_earthquakes')

        # Update success status
        cron_job.status = 'success'
        cron_job.success_count += 1
        cron_job.run_count += 1
        cron_job.last_result = f"Successfully fetched data at {timezone.now()}"
        cron_job.save()

        logger.info("Earthquake data fetch completed successfully")
        return "success"

    except Exception as e:
        logger.error(f"Error fetching earthquake data: {str(e)}")

        # Update error status
        try:
            cron_job = CronJob.objects.get(name='Fetch Earthquakes')
            cron_job.status = 'failed'
            cron_job.error_count += 1
            cron_job.run_count += 1
            cron_job.last_result = f"Error: {str(e)}"
            cron_job.save()
        except:
            pass

        return f"error: {str(e)}"
