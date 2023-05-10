from __future__ import absolute_import, unicode_literals

import os
from multiprocessing import cpu_count

from celery import Celery

from . import settings

# TODO:  RUN CELERY WITH - celery -A core.celery worker --pool=solo -l info

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.conf.enable_utc = False
app.conf.update(timezone="Asia/Karachi")
app.config_from_object(settings, namespace='CELERY')
app.autodiscover_tasks()
app.conf.worker_concurrency = 4  # number of worker processes to spawn
app.conf.update(
    worker_concurrency=cpu_count(),
    task_serializer='json',
    result_serializer='json',
    accept_content=['json']
)


@app.task(bind=True)
def test_task(self):
    print(f'Request: {self.request!r}')
