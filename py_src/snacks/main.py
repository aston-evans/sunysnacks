from snacks.db import app
from snacks.routes import router

app.include_router(router)
