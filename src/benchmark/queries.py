QUERIES = {
    "point_lookup": """
        MATCH (p:Person {id: $person_id})
        RETURN p.id, p.name, p.age
    """,

    "knows_lookup": """
        MATCH (p:Person {id: $person_id})-[:KNOWS]->(friend)
        RETURN friend.id, friend.name
    """,

    "person_company_city": """
        MATCH (p:Person {id: $person_id})
        OPTIONAL MATCH (p)-[:WORKS_AT]->(c:Company)
        OPTIONAL MATCH (p)-[:LIVES_IN]->(city:City)
        RETURN p.name, c.name, city.name
    """,

    "two_hop_traversal": """
        MATCH (p:Person {id: $person_id})
              -[:KNOWS]->(friend)
              -[:WORKS_AT]->(company)
        RETURN friend.name, company.name
    """,

    "company_aggregation": """
        MATCH (p:Person)-[:WORKS_AT]->(c:Company)
        RETURN c.name, count(p) AS employee_count
        ORDER BY employee_count DESC
    """,

    "short_path": """
        MATCH (a:Person {id: $source_id})
              -[:KNOWS*1..4]-(b:Person {id: $target_id})
        RETURN count(*) AS paths
    """,
}


DEFAULT_PARAMS = {
    "person_id": 42,
    "source_id": 1,
    "target_id": 100,
}