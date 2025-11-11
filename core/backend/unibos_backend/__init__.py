# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    # Celery is optional - the app can run without it
    celery_app = None
    __all__ = ()

__version__ = '1.0.0'