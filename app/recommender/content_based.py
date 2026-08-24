from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


class ContentBasedRecommender:
    REQUIRED_COLUMNS = {
    "article_id",
    "prod_name",
    "product_type_name",
    "product_group_name",
    "colour_group_name",
    "department_name",
    "section_name",
    "garment_group_name",
    "detail_desc",
    "image_url",
    "combined_features",
    }

    def __init__(self, products_path: str | Path):
        self.products_path = Path(products_path)

        self.products = self._load_products()
        self.vectorizer = self._create_vectorizer()

        self.tfidf_matrix = self.vectorizer.fit_transform(
            self.products["combined_features"]
        )

        self.product_indices = {
            article_id: index
            for index, article_id
            in enumerate(self.products["article_id"])
        }

    def _load_products(self) -> pd.DataFrame:
        if not self.products_path.exists():
            raise FileNotFoundError(
                f"Datoteka proizvoda ne postoji: "
                f"{self.products_path}"
            )

        products = pd.read_csv(
            self.products_path,
            dtype={"article_id": str},
            keep_default_na=False,
        )

        missing_columns = (
            self.REQUIRED_COLUMNS - set(products.columns)
        )

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))

            raise ValueError(
                f"U skupu podataka nedostaju stupci: {missing}"
            )

        products = products.drop_duplicates(
            subset="article_id",
            keep="first",
        )

        products["article_id"] = (
            products["article_id"]
            .astype(str)
            .str.strip()
        )

        products["prod_name"] = (
            products["prod_name"]
            .astype(str)
            .str.strip()
        )

        products["combined_features"] = (
            products["combined_features"]
            .astype(str)
            .str.strip()
        )

        products = products[
            (products["article_id"] != "")
            & (products["prod_name"] != "")
            & (products["combined_features"] != "")
        ]

        if products.empty:
            raise ValueError(
                "Skup podataka ne sadrži valjane proizvode."
            )

        return products.reset_index(drop=True)

    def _create_vectorizer(self) -> TfidfVectorizer:
        return TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=20_000,
        )

    def get_similar_products(
        self,
        article_id: str,
        number_of_results: int = 5,
    ) -> list[dict]:

        if number_of_results < 1:
            raise ValueError(
                        "Broj preporuka mora biti veći od nule."
                )
        
        article_id = str(article_id)

        matching_rows = self.products.index[
            self.products["article_id"] == article_id
        ].tolist()

        if not matching_rows:
            raise ValueError(
                f"Proizvod s ID-em {article_id} ne postoji."
            )

        selected_index = matching_rows[0]

        similarity_scores = linear_kernel(
            self.tfidf_matrix[selected_index:selected_index + 1],
            self.tfidf_matrix,
        ).flatten()

        ranked_indices = similarity_scores.argsort()[::-1]

        selected_name = (
        self.products.iloc[selected_index]["prod_name"]
        .strip()
        .lower()
        )

        recommended_indices = []
        used_product_names = {selected_name}

        for index in ranked_indices:
            product_name = (
                self.products.iloc[index]["prod_name"]
                .strip()
                .lower()
            )

            if index == selected_index:
                continue

            if product_name in used_product_names:
                continue

            recommended_indices.append(index)
            used_product_names.add(product_name)

            if len(recommended_indices) == number_of_results:
                break

        recommendations = self.products.iloc[recommended_indices][
            [
                "article_id",
                "prod_name",
                "product_type_name",
                "product_group_name",
                "colour_group_name",
                "detail_desc",
                "image_url",
            ]
        ].copy()

        recommendations["similarity_score"] = [
            round(float(similarity_scores[index]), 4)
            for index in recommended_indices
        ]

        return recommendations.to_dict(orient="records")

    def get_personalized_recommendations(
        self,
        interactions: list[dict],
        number_of_results: int = 10,
    ) -> list[dict]:

        if number_of_results < 1:
                raise ValueError(
                    "Broj preporuka mora biti veći od nule."
                )
        
        interaction_weights = {
            "view": 1,
            "like": 3,
            "purchase": 5,
        }

        product_weights = {}

        for interaction in interactions:
            article_id = str(interaction["article_id"])
            interaction_type = interaction["interaction_type"]

            if article_id not in self.product_indices:
                continue

            weight = interaction_weights.get(interaction_type)

            if weight is None:
                continue

            product_weights[article_id] = (
                product_weights.get(article_id, 0) + weight
            )

        if not product_weights:
            return []

        interacted_indices = [
            self.product_indices[article_id]
            for article_id in product_weights
        ]

        weights = np.array(
            list(product_weights.values()),
            dtype=float,
        )

        selected_vectors = self.tfidf_matrix[interacted_indices]

        weighted_vectors = selected_vectors.multiply(
            weights[:, np.newaxis]
        )

        user_profile = np.asarray(
            weighted_vectors.sum(axis=0) / weights.sum()
        )

        similarity_scores = linear_kernel(
            user_profile,
            self.tfidf_matrix,
        ).flatten()

        ranked_indices = similarity_scores.argsort()[::-1]

        excluded_indices = set(interacted_indices)
        recommended_indices = []
        used_product_names = set()

        for index in ranked_indices:
            if index in excluded_indices:
                continue

            product_name = (
                self.products.iloc[index]["prod_name"]
                .strip()
                .lower()
            )

            if product_name in used_product_names:
                continue

            recommended_indices.append(index)
            used_product_names.add(product_name)

            if len(recommended_indices) == number_of_results:
                break

        recommendations = self.products.iloc[
            recommended_indices
        ][
            [
                "article_id",
                "prod_name",
                "product_type_name",
                "product_group_name",
                "colour_group_name",
                "detail_desc",
                "image_url",
            ]
        ].copy()

        recommendations["similarity_score"] = [
            round(float(similarity_scores[index]), 4)
            for index in recommended_indices
        ]

        return recommendations.to_dict(orient="records")