import csv
import random
from pathlib import Path


SEED = 42

NUM_PERSONS = 500
NUM_COMPANIES = 100
NUM_CITIES = 50
NUM_KNOWS = 2000

DATA_DIR = Path("data")


def generate_dataset():
    random.seed(SEED)
    DATA_DIR.mkdir(exist_ok=True)

    # -------------------------
    # Persons
    # -------------------------
    with open(DATA_DIR / "persons.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "name", "age"])

        for person_id in range(1, NUM_PERSONS + 1):
            writer.writerow([
                person_id,
                f"Person_{person_id}",
                random.randint(18, 70),
            ])

    # -------------------------
    # Companies
    # -------------------------
    with open(DATA_DIR / "companies.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "name"])

        for company_id in range(1, NUM_COMPANIES + 1):
            writer.writerow([
                company_id,
                f"Company_{company_id}",
            ])

    # -------------------------
    # Cities
    # -------------------------
    with open(DATA_DIR / "cities.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "name"])

        for city_id in range(1, NUM_CITIES + 1):
            writer.writerow([
                city_id,
                f"City_{city_id}",
            ])

    # -------------------------
    # KNOWS relationships
    # -------------------------
    relationships = set()

    while len(relationships) < NUM_KNOWS:
        source = random.randint(1, NUM_PERSONS)
        target = random.randint(1, NUM_PERSONS)

        if source != target:
            relationships.add((source, target))

    with open(DATA_DIR / "knows.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["source_id", "target_id"])

        for source, target in sorted(relationships):
            writer.writerow([source, target])

    # -------------------------
    # WORKS_AT relationships
    # -------------------------
    with open(DATA_DIR / "works_at.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["person_id", "company_id"])

        for person_id in range(1, NUM_PERSONS + 1):
            company_id = random.randint(1, NUM_COMPANIES)
            writer.writerow([person_id, company_id])

    # -------------------------
    # LIVES_IN relationships
    # -------------------------
    with open(DATA_DIR / "lives_in.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["person_id", "city_id"])

        for person_id in range(1, NUM_PERSONS + 1):
            city_id = random.randint(1, NUM_CITIES)
            writer.writerow([person_id, city_id])

    # -------------------------
    # Summary
    # -------------------------
    print("Dataset generated successfully.")
    print(f"Persons: {NUM_PERSONS}")
    print(f"Companies: {NUM_COMPANIES}")
    print(f"Cities: {NUM_CITIES}")
    print(f"KNOWS relationships: {len(relationships)}")
    print(f"WORKS_AT relationships: {NUM_PERSONS}")
    print(f"LIVES_IN relationships: {NUM_PERSONS}")


if __name__ == "__main__":
    generate_dataset()