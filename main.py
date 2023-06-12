from neo4j import GraphDatabase
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Connect to Neo4j
driver = GraphDatabase.driver("neo4j+s://a71ad3ae.databases.neo4j.io", auth=("neo4j", "JYzNlAikmiFLjlTocP1c15qtT4St9oyIK-ZeIzEKlVo"))


def get_user_item_matrix():
    with driver.session() as session:
        query = """
        MATCH (u:User)-[r:INTERACTED_WITH]->(i:Item)
        RETURN u.id as user_id, i.id as item_id
        """
        result = session.run(query)
        user_ids = []
        item_ids = []
        for record in result:
            user_ids.append(record["user_id"])
            item_ids.append(record["item_id"])

        distinct_users = list(set(user_ids))
        distinct_items = list(set(item_ids))

        user_id_map = {user_id: idx for idx, user_id in enumerate(distinct_users)}
        item_id_map = {item_id: idx for idx, item_id in enumerate(distinct_items)}

        ui_matrix = np.zeros((len(distinct_users), len(distinct_items)))

        for user_id, item_id in zip(user_ids, item_ids):
            user_idx = user_id_map[user_id]
            item_idx = item_id_map[item_id]
            ui_matrix[user_idx, item_idx] = 1

        return ui_matrix, distinct_users, distinct_items


def get_similar_users(user_id, ui_matrix, distinct_users):
    target_user_idx = distinct_users.index(user_id)
    similarities = cosine_similarity(ui_matrix[target_user_idx].reshape(1, -1), ui_matrix)[0]
    recommended_users = [(distinct_users[i], similarities[i]) for i in range(len(similarities)) if i != target_user_idx]
    recommended_users.sort(key=lambda x: x[1], reverse=True)
    return recommended_users


def get_recommendations(user_id, similar_users, ui_matrix, distinct_items, top_n=5):
    target_user_idx = unique_users.index(user_id)
    target_user_interactions = ui_matrix[target_user_idx]
    recommended_users = []

    for item_idx in range(len(distinct_items)):
        if target_user_interactions[item_idx] == 0:
            weighted_sum = 0
            similarity_sum = 0

            for user, similarity in similar_users:
                user_idx = unique_users.index(user)
                weighted_sum += similarity * ui_matrix[user_idx, item_idx]
                similarity_sum += similarity

            if similarity_sum > 0:
                recommendation_score = weighted_sum / similarity_sum
                recommended_users.append((distinct_items[item_idx], recommendation_score))

    recommended_users.sort(key=lambda x: x[1], reverse=True)
    return recommended_users[:top_n]


# Example usage
target_user_id = "user1"
user_item_matrix, unique_users, unique_items = get_user_item_matrix()
similar_users = get_similar_users(target_user_id, user_item_matrix, unique_users)
recommendations = get_recommendations(target_user_id, similar_users, user_item_matrix, unique_items)
print(recommendations)
