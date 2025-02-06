from snacks.routes import router
from snacks.db import app


app.include_router(router)

