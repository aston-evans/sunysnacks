from snacks.routes import router
from snacks.db import app
from snacks.auth import authrouter


app.include_router(router)
app.include_router(authrouter)
