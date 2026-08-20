import csv
import time
from pathlib import Path

from falkordb import FalkorDB
from neo4j import GraphDatabase


DATA_DIR = Path("data")
FALKORDB_GRAPH = "benchmark"


def read_csv(filename):
    with open(DATA_DIR / filename, newline="") as file:
        return list(csv.DictReader(file))


def load_database(
    uri,
    username=None,
    password=None,
    database_name=None,
    name="Database",
):
    auth = (username, password) if username and password else None

    driver = GraphDatabase.driver(
        uri,
        auth=auth,
    )

    try:
        driver.verify_connectivity()

        start = time.perf_counter()

        session_kwargs = {}

        if database_name:
            session_kwargs["database"] = database_name

        with driver.session(**session_kwargs) as session:

            # Clear existing graph
            session.run(
                "MATCH (n) DETACH DELETE n"
            ).consume()

            # -------------------------
            # Persons
            # -------------------------
            persons = read_csv("persons.csv")

            session.run(
                """
                UNWIND $rows AS row
                CREATE (:Person {
                    id: toInteger(row.id),
                    name: row.name,
                    age: toInteger(row.age)
                })
                """,
                rows=persons,
            ).consume()

            # -------------------------
            # Companies
            # -------------------------
            companies = read_csv("companies.csv")

            session.run(
                """
                UNWIND $rows AS row
                CREATE (:Company {
                    id: toInteger(row.id),
                    name: row.name
                })
                """,
                rows=companies,
            ).consume()

            # -------------------------
            # Cities
            # -------------------------
            cities = read_csv("cities.csv")

            session.run(
                """
                UNWIND $rows AS row
                CREATE (:City {
                    id: toInteger(row.id),
                    name: row.name
                })
                """,
                rows=cities,
            ).consume()

            # -------------------------
            # KNOWS
            # -------------------------
            knows = read_csv("knows.csv")

            session.run(
                """
                UNWIND $rows AS row
                MATCH (a:Person {
                    id: toInteger(row.source_id)
                })
                MATCH (b:Person {
                    id: toInteger(row.target_id)
                })
                CREATE (a)-[:KNOWS]->(b)
                """,
                rows=knows,
            ).consume()

            # -------------------------
            # WORKS_AT
            # -------------------------
            works_at = read_csv("works_at.csv")

            session.run(
                """
                UNWIND $rows AS row
                MATCH (p:Person {
                    id: toInteger(row.person_id)
                })
                MATCH (c:Company {
                    id: toInteger(row.company_id)
                })
                CREATE (p)-[:WORKS_AT]->(c)
                """,
                rows=works_at,
            ).consume()

            # -------------------------
            # LIVES_IN
            # -------------------------
            lives_in = read_csv("lives_in.csv")

            session.run(
                """
                UNWIND $rows AS row
                MATCH (p:Person {
                    id: toInteger(row.person_id)
                })
                MATCH (c:City {
                    id: toInteger(row.city_id)
                })
                CREATE (p)-[:LIVES_IN]->(c)
                """,
                rows=lives_in,
            ).consume()

        elapsed = time.perf_counter() - start

        print(
            f"{name} loaded successfully in "
            f"{elapsed:.4f} seconds."
        )

    finally:
        driver.close()


def load_falkordb():
    db = FalkorDB(
        host="localhost",
        port=6379,
    )

    graph = db.select_graph(FALKORDB_GRAPH)

    start = time.perf_counter()

    # -------------------------
    # Clear existing graph
    # -------------------------
    try:
        graph.delete()
    except Exception:
        pass

    graph = db.select_graph(FALKORDB_GRAPH)

    # -------------------------
    # Persons
    # -------------------------
    persons = read_csv("persons.csv")

    graph.query(
        """
        UNWIND $rows AS row
        CREATE (:Person {
            id: row.id,
            name: row.name,
            age: row.age
        })
        """,
        params={
            "rows": [
                {
                    "id": int(row["id"]),
                    "name": row["name"],
                    "age": int(row["age"]),
                }
                for row in persons
            ]
        },
    )

    # -------------------------
    # Companies
    # -------------------------
    companies = read_csv("companies.csv")

    graph.query(
        """
        UNWIND $rows AS row
        CREATE (:Company {
            id: row.id,
            name: row.name
        })
        """,
        params={
            "rows": [
                {
                    "id": int(row["id"]),
                    "name": row["name"],
                }
                for row in companies
            ]
        },
    )

    # -------------------------
    # Cities
    # -------------------------
    cities = read_csv("cities.csv")

    graph.query(
        """
        UNWIND $rows AS row
        CREATE (:City {
            id: row.id,
            name: row.name
        })
        """,
        params={
            "rows": [
                {
                    "id": int(row["id"]),
                    "name": row["name"],
                }
                for row in cities
            ]
        },
    )

    # -------------------------
    # KNOWS
    # -------------------------
    knows = read_csv("knows.csv")

    graph.query(
        """
        UNWIND $rows AS row
        MATCH (a:Person {id: row.source_id})
        MATCH (b:Person {id: row.target_id})
        CREATE (a)-[:KNOWS]->(b)
        """,
        params={
            "rows": [
                {
                    "source_id": int(row["source_id"]),
                    "target_id": int(row["target_id"]),
                }
                for row in knows
            ]
        },
    )

    # -------------------------
    # WORKS_AT
    # -------------------------
    works_at = read_csv("works_at.csv")

    graph.query(
        """
        UNWIND $rows AS row
        MATCH (p:Person {id: row.person_id})
        MATCH (c:Company {id: row.company_id})
        CREATE (p)-[:WORKS_AT]->(c)
        """,
        params={
            "rows": [
                {
                    "person_id": int(row["person_id"]),
                    "company_id": int(row["company_id"]),
                }
                for row in works_at
            ]
        },
    )

    # -------------------------
    # LIVES_IN
    # -------------------------
    lives_in = read_csv("lives_in.csv")

    graph.query(
        """
        UNWIND $rows AS row
        MATCH (p:Person {id: row.person_id})
        MATCH (c:City {id: row.city_id})
        CREATE (p)-[:LIVES_IN]->(c)
        """,
        params={
            "rows": [
                {
                    "person_id": int(row["person_id"]),
                    "city_id": int(row["city_id"]),
                }
                for row in lives_in
            ]
        },
    )

    elapsed = time.perf_counter() - start

    print(
        f"FalkorDB loaded successfully in "
        f"{elapsed:.4f} seconds."
    )


if __name__ == "__main__":

    # =========================
    # Neo4j
    # =========================
    load_database(
        uri="bolt://localhost:7687",
        username="neo4j",
        password="benchmarkpassword",
        database_name="neo4j",
        name="Neo4j",
    )

    # =========================
    # Memgraph
    # =========================
    load_database(
        uri="bolt://localhost:7688",
        name="Memgraph",
    )

    # =========================
    # FalkorDB
    # =========================
    load_falkordb()