import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

uri = os.getenv("COGNODB_URI")
username = os.getenv("COGNODB_USERNAME")
password = os.getenv("COGNODB_PASSWORD")

if not uri or not username or not password:
    raise RuntimeError("Missing CognoDB environment variables")

driver = GraphDatabase.driver(
    uri,
    auth=(username, password)
)

try:
    driver.verify_connectivity()
    print("Connected to CognoDB!")

    with driver.session() as session:
        result = session.run("RETURN 1 AS result")
        record = result.single()
        print(f"Cypher result: {record['result']}")

finally:
    driver.close()