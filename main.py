from fastapi import FastAPI
import Models.todos_model as todos_model
from Database.database import engine
from scalar_fastapi import get_scalar_api_reference
from Auth import auth
from Routers import todos


app = FastAPI()

todos_model.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title
    )
