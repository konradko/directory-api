web: python manage.py migrate --noinput && python manage.py distributed_elasticsearch_migrate && waitress-serve --port=$PORT conf.wsgi:application
celery_worker: celery -A api worker -l info
celery_beat: celery -A api beat -l info -S django
