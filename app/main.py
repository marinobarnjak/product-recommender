from fastapi import (
    Depends,
    FastAPI,
    Form,
    HTTPException,
    Query,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.requests import Request

from app import models, schemas
from app.database import engine, get_db
from app.recommender.content_based import ContentBasedRecommender

app = FastAPI(
    title="Sustav preporuke proizvoda",
    description=(
        "Content-based sustav preporuke proizvoda "
        "temeljen na TF-IDF-u i kosinusnoj sličnosti."
    ),
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

templates = Jinja2Templates(
    directory="app/templates"
)

models.Base.metadata.create_all(bind=engine)
recommender = ContentBasedRecommender("data/products.csv")


@app.get("/")
def home():
    return {
        "message": "Sustav preporuke proizvoda radi",
        "number_of_products": len(recommender.products),
    }


@app.get("/products")
def get_products(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    selected_products = recommender.products.iloc[
        offset:offset + limit
    ]

    return selected_products[
        [
            "article_id",
            "prod_name",
            "product_type_name",
            "product_group_name",
            "colour_group_name",
            "detail_desc",
            "image_url",
        ]
    ].to_dict(orient="records")


@app.get("/products/{article_id}")
def get_product(article_id: str):
    matching_products = recommender.products[
        recommender.products["article_id"] == article_id
    ]

    if matching_products.empty:
        raise HTTPException(
            status_code=404,
            detail="Proizvod nije pronađen.",
        )

    product = matching_products.iloc[0]

    return {
        "article_id": product["article_id"],
        "prod_name": product["prod_name"],
        "product_type_name": product["product_type_name"],
        "product_group_name": product["product_group_name"],
        "colour_group_name": product["colour_group_name"],
        "department_name": product["department_name"],
        "section_name": product["section_name"],
        "garment_group_name": product["garment_group_name"],
        "detail_desc": product["detail_desc"],
        "image_url": product["image_url"],
    }


@app.get("/products/{article_id}/similar")
def get_similar_products(
    article_id: str,
    limit: int = Query(default=5, ge=1, le=20),
):
    try:
        recommendations = recommender.get_similar_products(
            article_id=article_id,
            number_of_results=limit,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    return {
        "article_id": article_id,
        "number_of_recommendations": len(recommendations),
        "recommendations": recommendations,
    }

@app.post(
    "/users",
    response_model=schemas.UserResponse,
    status_code=201,
)
def create_user(
    user_data: schemas.UserCreate,
    database: Session = Depends(get_db),
):
    user = models.User(username=user_data.username)

    database.add(user)

    try:
        database.commit()
        database.refresh(user)
    except IntegrityError:
        database.rollback()

        raise HTTPException(
            status_code=409,
            detail="Korisničko ime već postoji.",
        )

    return user


@app.get(
    "/users",
    response_model=list[schemas.UserResponse],
)
def get_users(
    database: Session = Depends(get_db),
):
    return database.query(models.User).all()


@app.post(
    "/interactions",
    response_model=schemas.InteractionResponse,
    status_code=201,
)
def create_interaction(
    interaction_data: schemas.InteractionCreate,
    database: Session = Depends(get_db),
):
    user = database.get(
        models.User,
        interaction_data.user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Korisnik nije pronađen.",
        )

    matching_product = recommender.products[
        recommender.products["article_id"]
        == interaction_data.article_id
    ]

    if matching_product.empty:
        raise HTTPException(
            status_code=404,
            detail="Proizvod nije pronađen.",
        )

    interaction = models.Interaction(
        user_id=interaction_data.user_id,
        article_id=interaction_data.article_id,
        interaction_type=interaction_data.interaction_type,
    )

    database.add(interaction)
    database.commit()
    database.refresh(interaction)

    return interaction


@app.get(
    "/users/{user_id}/interactions",
    response_model=list[schemas.InteractionResponse],
)
def get_user_interactions(
    user_id: int,
    database: Session = Depends(get_db),
):
    user = database.get(models.User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Korisnik nije pronađen.",
        )

    return (
        database.query(models.Interaction)
        .filter(models.Interaction.user_id == user_id)
        .order_by(models.Interaction.created_at.desc())
        .all()
    )

@app.get("/users/{user_id}/recommendations")
def get_personalized_recommendations(
    user_id: int,
    limit: int = Query(default=10, ge=1, le=50),
    database: Session = Depends(get_db),
):
    user = database.get(models.User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Korisnik nije pronađen.",
        )

    stored_interactions = (
        database.query(models.Interaction)
        .filter(models.Interaction.user_id == user_id)
        .all()
    )

    interactions = [
        {
            "article_id": interaction.article_id,
            "interaction_type": interaction.interaction_type,
        }
        for interaction in stored_interactions
    ]

    recommendations = (
        recommender.get_personalized_recommendations(
            interactions=interactions,
            number_of_results=limit,
        )
    )

    if not recommendations:
        return {
            "user_id": user_id,
            "message": (
                "Korisnik još nema dovoljno aktivnosti "
                "za personalizirane preporuke."
            ),
            "recommendations": [],
        }

    return {
        "user_id": user_id,
        "number_of_interactions": len(interactions),
        "number_of_recommendations": len(recommendations),
        "recommendations": recommendations,
    }

@app.get(
    "/shop",
    response_class=HTMLResponse,
)
def shop_page(
    request: Request,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=24, ge=1, le=48),
):
    products = recommender.products.iloc[
        offset:offset + limit
    ].to_dict(orient="records")

    next_offset = offset + limit
    previous_offset = max(offset - limit, 0)

    return templates.TemplateResponse(
        request=request,
        name="products.html",
        context={
            "products": products,
            "offset": offset,
            "limit": limit,
            "next_offset": next_offset,
            "previous_offset": previous_offset,
            "total_products": len(recommender.products),
        },
    )

@app.get(
    "/shop/products/{article_id}",
    response_class=HTMLResponse,
)
def product_detail_page(
    article_id: str,
    request: Request,
    user_id: int = Query(default=1, ge=1),
    database: Session = Depends(get_db),
):
    user = database.get(models.User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Korisnik nije pronađen.",
        )

    matching_products = recommender.products[
        recommender.products["article_id"] == article_id
    ]

    if matching_products.empty:
        raise HTTPException(
            status_code=404,
            detail="Proizvod nije pronađen.",
        )

    product = matching_products.iloc[0].to_dict()

    existing_view = (
        database.query(models.Interaction)
        .filter(
            models.Interaction.user_id == user_id,
            models.Interaction.article_id == article_id,
            models.Interaction.interaction_type == "view",
        )
        .first()
    )

    if existing_view is None:
        view_interaction = models.Interaction(
            user_id=user_id,
            article_id=article_id,
            interaction_type="view",
        )

        database.add(view_interaction)
        database.commit()

    similar_products = recommender.get_similar_products(
        article_id=article_id,
        number_of_results=4,
    )

    return templates.TemplateResponse(
        request=request,
        name="product_detail.html",
        context={
            "product": product,
            "similar_products": similar_products,
            "user_id": user_id,
        },
    )

@app.post("/shop/interactions")
def create_shop_interaction(
    user_id: int = Form(...),
    article_id: str = Form(...),
    interaction_type: str = Form(...),
    database: Session = Depends(get_db),
):
    allowed_types = {"like", "purchase"}

    if interaction_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Nedozvoljena vrsta interakcije.",
        )

    user = database.get(models.User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Korisnik nije pronađen.",
        )

    if article_id not in recommender.product_indices:
        raise HTTPException(
            status_code=404,
            detail="Proizvod nije pronađen.",
        )

    existing_interaction = (
        database.query(models.Interaction)
        .filter(
            models.Interaction.user_id == user_id,
            models.Interaction.article_id == article_id,
            models.Interaction.interaction_type
            == interaction_type,
        )
        .first()
    )

    if existing_interaction is None:
        interaction = models.Interaction(
            user_id=user_id,
            article_id=article_id,
            interaction_type=interaction_type,
        )

        database.add(interaction)
        database.commit()

    return RedirectResponse(
        url=(
            f"/shop/products/{article_id}"
            f"?user_id={user_id}"
        ),
        status_code=303,
    )

@app.get(
    "/shop/recommendations/{user_id}",
    response_class=HTMLResponse,
)
def recommendations_page(
    user_id: int,
    request: Request,
    database: Session = Depends(get_db),
):
    user = database.get(models.User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Korisnik nije pronađen.",
        )

    stored_interactions = (
        database.query(models.Interaction)
        .filter(models.Interaction.user_id == user_id)
        .all()
    )

    interactions = [
        {
            "article_id": interaction.article_id,
            "interaction_type": interaction.interaction_type,
        }
        for interaction in stored_interactions
    ]

    recommendations = (
        recommender.get_personalized_recommendations(
            interactions=interactions,
            number_of_results=12,
        )
    )

    return templates.TemplateResponse(
        request=request,
        name="recommendations.html",
        context={
            "user": user,
            "recommendations": recommendations,
            "number_of_interactions": len(interactions),
        },
    )