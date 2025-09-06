from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware #What is CORSMiddleware
from core.config import settings

app = FastAPI(
    title = "Choose Your Own Adventure API",
    Description = "API to cure boredom",
    version = "0.1.0",
    docs = "/docs",
    redoc_url = "/redoc"
)
#Automatic documentation due to FastAPI

app.add_middleware(
    CORSMiddleware,
    allow_origins = settings.ALLOWED_ORIGINS,
    allow_credentials = True, #Allowing credentials
    allow_methods = ["*"], #Allowing all methods(GET,POST,PUT,PATCH etc.)
    allow_headers = ["*"], #Additional Information(Generally limited, but as base case currently allowing everything)
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
