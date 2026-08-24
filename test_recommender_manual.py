from app.recommender.content_based import ContentBasedRecommender


recommender = ContentBasedRecommender("data/products.csv")

selected_product = recommender.products.iloc[0]

print("\nOdabrani proizvod:")
print(f"ID: {selected_product['article_id']}")
print(f"Naziv: {selected_product['prod_name']}")
print(f"Vrsta: {selected_product['product_type_name']}")
print(f"Boja: {selected_product['colour_group_name']}")

recommendations = recommender.get_similar_products(
    article_id=selected_product["article_id"],
    number_of_results=5,
)

print("\nPreporučeni proizvodi:")

for position, product in enumerate(recommendations, start=1):
    print(
        f"{position}. {product['prod_name']} | "
        f"{product['product_type_name']} | "
        f"{product['colour_group_name']} | "
        f"sličnost: {product['similarity_score']}"
    )