from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.schemas import CreateUserRequest, User


def create_app() -> FastAPI:
    app = FastAPI(title="Contract Testing Demo API", version="0.1.0")

    users_db: dict[int, User] = {
        1: User(id=1, name="Alice", email="alice@example.com"),
    }
    next_id = 2

    class ProviderStateRequest(BaseModel):
        state: str

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/users/{user_id}", response_model=User)
    def get_user(user_id: int) -> User:
        user = users_db.get(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @app.post("/users", response_model=User, status_code=201)
    def create_user(payload: CreateUserRequest) -> User:
        nonlocal next_id
        user = User(id=next_id, name=payload.name, email=payload.email)
        users_db[user.id] = user
        next_id += 1
        return user

    @app.post("/_pact/provider_states", status_code=204)
    def setup_provider_state(payload: ProviderStateRequest) -> None:
        nonlocal users_db, next_id
        if payload.state == "a user with id 1 exists":
            users_db = {
                1: User(id=1, name="Alice", email="alice@example.com"),
            }
            next_id = 2
            return
        if payload.state == "user creation is available":
            users_db = {
                1: User(id=1, name="Alice", email="alice@example.com"),
            }
            next_id = 2
            return
        raise HTTPException(status_code=400, detail=f"Unknown state: {payload.state}")

    return app


app = create_app()
