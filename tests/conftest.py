import pandas as pd
import pytest

from app.recommender.content_based import (
    ContentBasedRecommender,
)


@pytest.fixture
def sample_products_path(tmp_path):
    products = pd.DataFrame(
        [
            {
                "article_id": "0000000001",
                "prod_name": "Runner Pro",
                "product_type_name": "Sneakers",
                "product_group_name": "Shoes",
                "colour_group_name": "Red",
                "department_name": "Sport",
                "section_name": "Running",
                "garment_group_name": "Footwear",
                "detail_desc": (
                    "Lightweight running shoes with mesh."
                ),
                "image_url": "",
                "combined_features": (
                    "runner pro sneakers shoes red sport "
                    "running footwear lightweight mesh"
                ),
            },
            {
                "article_id": "0000000002",
                "prod_name": "Runner Pro",
                "product_type_name": "Sneakers",
                "product_group_name": "Shoes",
                "colour_group_name": "Blue",
                "department_name": "Sport",
                "section_name": "Running",
                "garment_group_name": "Footwear",
                "detail_desc": (
                    "Lightweight running shoes in blue."
                ),
                "image_url": "",
                "combined_features": (
                    "runner pro sneakers shoes blue sport "
                    "running footwear lightweight"
                ),
            },
            {
                "article_id": "0000000003",
                "prod_name": "Trail Master",
                "product_type_name": "Sneakers",
                "product_group_name": "Shoes",
                "colour_group_name": "Black",
                "department_name": "Sport",
                "section_name": "Outdoor",
                "garment_group_name": "Footwear",
                "detail_desc": (
                    "Outdoor trail running shoes with grip."
                ),
                "image_url": "",
                "combined_features": (
                    "trail master sneakers shoes black sport "
                    "outdoor running footwear grip"
                ),
            },
            {
                "article_id": "0000000004",
                "prod_name": "Urban Jacket",
                "product_type_name": "Jacket",
                "product_group_name": "Garment Upper body",
                "colour_group_name": "Black",
                "department_name": "Menswear",
                "section_name": "Jackets",
                "garment_group_name": "Outdoor",
                "detail_desc": (
                    "Black urban jacket with front zipper."
                ),
                "image_url": "",
                "combined_features": (
                    "urban jacket garment upper body black "
                    "menswear jackets outdoor front zipper"
                ),
            },
            {
                "article_id": "0000000005",
                "prod_name": "Winter Coat",
                "product_type_name": "Coat",
                "product_group_name": "Garment Upper body",
                "colour_group_name": "Black",
                "department_name": "Menswear",
                "section_name": "Jackets",
                "garment_group_name": "Outdoor",
                "detail_desc": (
                    "Warm winter coat for outdoor use."
                ),
                "image_url": "",
                "combined_features": (
                    "winter coat garment upper body black "
                    "menswear jackets outdoor warm"
                ),
            },
            {
                "article_id": "0000000006",
                "prod_name": "Basic Shirt",
                "product_type_name": "Shirt",
                "product_group_name": "Garment Upper body",
                "colour_group_name": "White",
                "department_name": "Menswear",
                "section_name": "Shirts",
                "garment_group_name": "Jersey",
                "detail_desc": "Basic white cotton shirt.",
                "image_url": "",
                "combined_features": (
                    "basic shirt garment upper body white "
                    "menswear shirts jersey cotton"
                ),
            },
        ]
    )

    products_path = tmp_path / "products.csv"
    products.to_csv(products_path, index=False)

    return products_path


@pytest.fixture
def recommender(sample_products_path):
    return ContentBasedRecommender(
        sample_products_path
    )