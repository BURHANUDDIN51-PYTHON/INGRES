from fastapi import FastAPI
from ingres_api.config import settings
from ingres_api.endpoints import chatbot

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.API_VERSION,
        debug=settings.DEBUG,
    )
    # Include Routers
    app.include_router(chatbot.router)
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
