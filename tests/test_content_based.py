import pandas as pd
import pytest

from app.recommender.content_based import (
    ContentBasedRecommender,
)


def test_loads_products(recommender):
    assert len(recommender.products) == 6
    assert recommender.tfidf_matrix.shape[0] == 6


def test_preserves_leading_zero_in_article_id(
    recommender,
):
    article_id = recommender.products.iloc[0][
        "article_id"
    ]

    assert article_id == "0000000001"


def test_returns_requested_number_of_recommendations(
    recommender,
):
    recommendations = recommender.get_similar_products(
        article_id="0000000001",
        number_of_results=3,
    )

    assert len(recommendations) == 3


def test_excludes_selected_product(recommender):
    recommendations = recommender.get_similar_products(
        article_id="0000000001",
        number_of_results=5,
    )

    recommended_ids = {
        product["article_id"]
        for product in recommendations
    }

    assert "0000000001" not in recommended_ids


def test_does_not_repeat_product_names(recommender):
    recommendations = recommender.get_similar_products(
        article_id="0000000001",
        number_of_results=5,
    )

    product_names = [
        product["prod_name"].strip().lower()
        for product in recommendations
    ]

    assert len(product_names) == len(set(product_names))
    assert "runner pro" not in product_names


def test_nonexistent_product_raises_error(recommender):
    with pytest.raises(
        ValueError,
        match="ne postoji",
    ):
        recommender.get_similar_products(
            article_id="9999999999",
        )


def test_zero_recommendations_raises_error(recommender):
    with pytest.raises(
        ValueError,
        match="veći od nule",
    ):
        recommender.get_similar_products(
            article_id="0000000001",
            number_of_results=0,
        )


def test_empty_interactions_return_empty_list(
    recommender,
):
    recommendations = (
        recommender.get_personalized_recommendations(
            interactions=[],
        )
    )

    assert recommendations == []


def test_unknown_interactions_are_ignored(
    recommender,
):
    interactions = [
        {
            "article_id": "0000000001",
            "interaction_type": "unknown",
        }
    ]

    recommendations = (
        recommender.get_personalized_recommendations(
            interactions=interactions,
        )
    )

    assert recommendations == []


def test_personalized_recommendations_exclude_interacted_products(
    recommender,
):
    interactions = [
        {
            "article_id": "0000000001",
            "interaction_type": "purchase",
        },
        {
            "article_id": "0000000004",
            "interaction_type": "view",
        },
    ]

    recommendations = (
        recommender.get_personalized_recommendations(
            interactions=interactions,
            number_of_results=4,
        )
    )

    recommended_ids = {
        product["article_id"]
        for product in recommendations
    }

    assert "0000000001" not in recommended_ids
    assert "0000000004" not in recommended_ids


def test_purchase_has_stronger_influence_than_view(
    recommender,
):
    interactions = [
        {
            "article_id": "0000000004",
            "interaction_type": "view",
        },
        {
            "article_id": "0000000001",
            "interaction_type": "purchase",
        },
    ]

    recommendations = (
        recommender.get_personalized_recommendations(
            interactions=interactions,
            number_of_results=1,
        )
    )

    assert len(recommendations) == 1
    assert (
        recommendations[0]["product_group_name"]
        == "Shoes"
    )


def test_missing_csv_file_raises_error(tmp_path):
    missing_file = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        ContentBasedRecommender(missing_file)


def test_missing_required_column_raises_error(
    tmp_path,
):
    invalid_products = pd.DataFrame(
        [
            {
                "article_id": "0000000001",
                "prod_name": "Test product",
            }
        ]
    )

    products_path = tmp_path / "invalid.csv"
    invalid_products.to_csv(products_path, index=False)

    with pytest.raises(
        ValueError,
        match="nedostaju stupci",
    ):
        ContentBasedRecommender(products_path)