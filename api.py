from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.api import router
from db.main import engine
from db.models import Base
from fastapi_pagination import Page, add_pagination, paginate

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title='ReaBar'
)

app.add_middleware(
	CORSMiddleware,
	allow_credentials=True,
	allow_origins=['*'],
	allow_methods=['*'],
	allow_headers=['*'],
)

app.include_router(router)
add_pagination(app)

