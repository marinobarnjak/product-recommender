from pathlib import Path

import pandas as pd
from datasets import load_dataset


NUMBER_OF_PRODUCTS = 5000
OUTPUT_PATH = Path("data/products.csv")

SELECTED_COLUMNS = [
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
]


def load_products() -> pd.DataFrame:
    print("Učitavanje proizvoda...")

    dataset = load_dataset(
        "Qdrant/hm_ecommerce_products",
        split="train",
        streaming=True,
    )

    sampled_products = (
        dataset
        .shuffle(seed=42, buffer_size=10_000)
        .take(NUMBER_OF_PRODUCTS)
    )

    products = pd.DataFrame(sampled_products)

    return products[SELECTED_COLUMNS]


def clean_products(products: pd.DataFrame) -> pd.DataFrame:
    products = products.copy()

    products = products.drop_duplicates(subset="article_id")
    products = products.dropna(subset=["article_id", "prod_name"])

    text_columns = [
        "prod_name",
        "product_type_name",
        "product_group_name",
        "colour_group_name",
        "department_name",
        "section_name",
        "garment_group_name",
        "detail_desc",
    ]

    products[text_columns] = products[text_columns].fillna("")

    products["combined_features"] = (
        products["prod_name"] + " " +
        products["product_type_name"] + " " +
        products["product_group_name"] + " " +
        products["colour_group_name"] + " " +
        products["department_name"] + " " +
        products["section_name"] + " " +
        products["garment_group_name"] + " " +
        products["detail_desc"]
    )

    products["combined_features"] = (
        products["combined_features"]
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    return products.reset_index(drop=True)


def save_products(products: pd.DataFrame) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    products.to_csv(OUTPUT_PATH, index=False)

    print(f"Spremljeno proizvoda: {len(products)}")
    print(f"Datoteka: {OUTPUT_PATH}")


def main() -> None:
    products = load_products()
    products = clean_products(products)
    save_products(products)

    print("\nPrvih pet proizvoda:")
    print(
        products[
            ["article_id", "prod_name", "product_type_name", "colour_group_name"]
        ].head()
    )


if __name__ == "__main__":
    main()