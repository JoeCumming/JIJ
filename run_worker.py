
import os
from app import celery, create_app

app = create_app(os.environ.get('APP_ENV', 'default'))
app.app_context().push()