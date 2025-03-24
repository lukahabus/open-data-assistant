"""
DCAT Test Script - Skript za testiranje DCAT funkcionalnosti.

Ova skripta omogućuje testiranje DCAT funkcionalnosti koristeći posebno pripremljeni
testni katalog koji sadrži raznovrsne skupove podataka s različitim karakteristikama.
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
import argparse

# Dodaj parent direktorij u sys.path za ispravno učitavanje modula
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Sada učitaj module
from dcat.dcat_metadata import (
    Catalog,
    Dataset,
    Distribution,
    DataService,
    DatasetSeries,
    CatalogRecord,
    DCATResource,
    load_catalog_from_json,
    save_catalog_to_json,
)


def load_test_catalog():
    """Učitaj testni DCAT katalog."""
    catalog_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "test_dcat_catalog.json"
    )

    if not os.path.exists(catalog_path):
        print(f"Greška: Testni katalog nije pronađen na putanji {catalog_path}.")
        sys.exit(1)

    print(f"Učitavanje testnog DCAT kataloga iz {catalog_path}...")
    return load_catalog_from_json(catalog_path)


def print_catalog_summary(catalog):
    """Ispiši sažetak kataloga."""
    print("\n=== SAŽETAK DCAT KATALOGA ===")
    print(f"ID: {catalog.id}")
    print(f"Naslov: {catalog.title}")
    print(f"Broj skupova podataka: {len(catalog.datasets)}")
    print(f"Broj servisa: {len(catalog.services)}")
    print(f"Broj serija skupova podataka: {len(catalog.dataset_series)}")
    print(f"Broj kataložnih zapisa: {len(catalog.records)}")

    print("\n--- Skupovi podataka ---")
    for dataset in catalog.datasets:
        print(
            f"- {dataset.id}: {dataset.title} ({len(dataset.distributions)} distribucija)"
        )

    print("\n--- Servisi ---")
    for service in catalog.services:
        print(f"- {service.id}: {service.title}")

    print("\n--- Serije skupova podataka ---")
    for series in catalog.dataset_series:
        print(f"- {series.id}: {series.title} ({len(series.datasets)} skupova)")


def test_dataset_search(catalog, query):
    """Testira pretraživanje skupova podataka po ključnim riječima."""
    print(f"\n=== PRETRAGA SKUPOVA PODATAKA: '{query}' ===")

    # Jednostavna implementacija pretraživanja teksta
    results = []
    for dataset in catalog.datasets:
        score = 0

        # Provjeri naslov
        if query.lower() in dataset.title.lower():
            score += 3

        # Provjeri opis
        if query.lower() in dataset.description.lower():
            score += 2

        # Provjeri ključne riječi
        for keyword in dataset.keywords:
            if query.lower() in keyword.lower():
                score += 1

        # Provjeri teme
        for theme in dataset.themes:
            if query.lower() in theme.lower():
                score += 1

        if score > 0:
            results.append((dataset, score))

    # Sortiraj prema score-u (relevantnosti)
    results.sort(key=lambda x: x[1], reverse=True)

    if not results:
        print("Nisu pronađeni rezultati za upit.")
        return

    for i, (dataset, score) in enumerate(results, 1):
        print(f"{i}. {dataset.title} (ID: {dataset.id}) - Relevantnost: {score}")
        print(f"   Opis: {dataset.description[:100]}...")
        print(f"   Ključne riječi: {', '.join(dataset.keywords)}")
        print()


def test_format_search(catalog, format_type):
    """Testira pretraživanje distribucija prema formatu."""
    print(f"\n=== PRETRAGA DISTRIBUCIJA PO FORMATU: '{format_type}' ===")

    results = []
    for dataset in catalog.datasets:
        for dist in dataset.distributions:
            if dist.format and dist.format.lower() == format_type.lower():
                results.append((dataset, dist))

    if not results:
        print(f"Nisu pronađene distribucije u formatu '{format_type}'.")
        return

    for i, (dataset, dist) in enumerate(results, 1):
        print(f"{i}. {dist.title} (ID: {dist.id})")
        print(f"   Skup podataka: {dataset.title}")
        print(f"   Format: {dist.format}")
        print(f"   Media type: {dist.media_type}")
        print(f"   URL za preuzimanje: {dist.download_url}")
        print()


def test_temporal_search(catalog, year):
    """Testira pretraživanje skupova podataka prema vremenskom pokriću."""
    print(f"\n=== PRETRAGA SKUPOVA PODATAKA PO GODINI: {year} ===")

    results = []
    for dataset in catalog.datasets:
        if dataset.temporal_coverage:
            start_year = (
                int(dataset.temporal_coverage.get("start_date", "").split("-")[0])
                if dataset.temporal_coverage.get("start_date")
                else None
            )
            end_year = (
                int(dataset.temporal_coverage.get("end_date", "").split("-")[0])
                if dataset.temporal_coverage.get("end_date")
                else None
            )

            if start_year and end_year and start_year <= year <= end_year:
                results.append(dataset)

    if not results:
        print(f"Nisu pronađeni skupovi podataka koji pokrivaju godinu {year}.")
        return

    for i, dataset in enumerate(results, 1):
        tc = dataset.temporal_coverage
        print(f"{i}. {dataset.title} (ID: {dataset.id})")
        print(f"   Vremensko pokriće: {tc.get('start_date')} do {tc.get('end_date')}")
        print(f"   Opis: {dataset.description[:100]}...")
        print()


def test_spatial_search(catalog, spatial_type):
    """Testira pretraživanje skupova podataka prema prostornom pokriću."""
    print(f"\n=== PRETRAGA SKUPOVA PODATAKA PO PROSTORNOM TIPU: '{spatial_type}' ===")

    results = []
    for dataset in catalog.datasets:
        if (
            dataset.spatial_coverage
            and dataset.spatial_coverage.get("type") == spatial_type
        ):
            results.append(dataset)

    if not results:
        print(f"Nisu pronađeni skupovi podataka s prostornim tipom '{spatial_type}'.")
        return

    for i, dataset in enumerate(results, 1):
        sc = dataset.spatial_coverage
        print(f"{i}. {dataset.title} (ID: {dataset.id})")
        print(f"   Prostorni tip: {sc.get('type')}")
        print(f"   Koordinate: {sc.get('coordinates')}")
        print()


def test_services_for_dataset(catalog, dataset_id):
    """Testira pronalaženje servisa koji koriste određeni skup podataka."""
    print(f"\n=== SERVISI KOJI KORISTE SKUP PODATAKA: '{dataset_id}' ===")

    dataset = next((d for d in catalog.datasets if d.id == dataset_id), None)
    if not dataset:
        print(f"Skup podataka s ID-om '{dataset_id}' nije pronađen.")
        return

    results = []
    for service in catalog.services:
        if dataset_id in service.serves_dataset:
            results.append(service)

    if not results:
        print(f"Nisu pronađeni servisi koji koriste skup podataka '{dataset_id}'.")
        return

    print(f"Skup podataka: {dataset.title} (ID: {dataset_id})")
    for i, service in enumerate(results, 1):
        print(f"{i}. {service.title} (ID: {service.id})")
        print(f"   Opis: {service.description}")
        print(f"   Endpoint URL: {service.endpoint_url}")
        print(f"   Tip servisa: {service.service_type}")
        print()


def test_related_datasets(catalog, dataset_id):
    """Testira pronalaženje povezanih skupova podataka kroz serije."""
    print(f"\n=== POVEZANI SKUPOVI PODATAKA ZA: '{dataset_id}' ===")

    dataset = next((d for d in catalog.datasets if d.id == dataset_id), None)
    if not dataset:
        print(f"Skup podataka s ID-om '{dataset_id}' nije pronađen.")
        return

    related_datasets = set()

    # Pronađi serije koje sadrže ovaj skup podataka
    related_series = [s for s in catalog.dataset_series if dataset_id in s.datasets]

    # Iz tih serija izvuci ostale skupove podataka
    for series in related_series:
        for ds_id in series.datasets:
            if ds_id != dataset_id:
                related_datasets.add(ds_id)

    if not related_datasets:
        print(f"Nisu pronađeni povezani skupovi podataka za '{dataset_id}'.")
        return

    print(f"Skup podataka: {dataset.title} (ID: {dataset_id})")
    print(f"Povezani skupovi podataka:")

    for ds_id in related_datasets:
        related = next((d for d in catalog.datasets if d.id == ds_id), None)
        if related:
            print(f"- {related.title} (ID: {related.id})")
            print(f"  Opis: {related.description[:100]}...")

            # Pronađi serije koje povezuju ove skupove
            connecting_series = [
                s
                for s in catalog.dataset_series
                if dataset_id in s.datasets and ds_id in s.datasets
            ]
            if connecting_series:
                print(
                    f"  Povezani kroz serije: {', '.join([s.title for s in connecting_series])}"
                )
            print()


def interactive_test_mode(catalog):
    """Pokreni interaktivni način testiranja."""
    while True:
        print("\n=== TESTIRANJE DCAT FUNKCIONALNOSTI ===")
        print("1. Prikaži sažetak kataloga")
        print("2. Pretraži skupove podataka")
        print("3. Pretraži distribucije prema formatu")
        print("4. Pretraži prema vremenskom pokriću")
        print("5. Pretraži prema prostornom tipu")
        print("6. Pronađi servise za skup podataka")
        print("7. Pronađi povezane skupove podataka")
        print("0. Izlaz")

        choice = input("\nOdabir: ")

        if choice == "0":
            print("Izlazak iz programa.")
            break

        elif choice == "1":
            print_catalog_summary(catalog)

        elif choice == "2":
            query = input("Unesite ključnu riječ za pretragu: ")
            test_dataset_search(catalog, query)

        elif choice == "3":
            format_type = input(
                "Unesite format za pretragu (npr. CSV, JSON, GeoJSON, PDF, XLSX): "
            )
            test_format_search(catalog, format_type)

        elif choice == "4":
            try:
                year = int(input("Unesite godinu za pretragu: "))
                test_temporal_search(catalog, year)
            except ValueError:
                print("Greška: Unesite valjanu godinu.")

        elif choice == "5":
            spatial_type = input("Unesite prostorni tip (Point, Polygon): ")
            test_spatial_search(catalog, spatial_type)

        elif choice == "6":
            dataset_id = input("Unesite ID skupa podataka: ")
            test_services_for_dataset(catalog, dataset_id)

        elif choice == "7":
            dataset_id = input("Unesite ID skupa podataka: ")
            test_related_datasets(catalog, dataset_id)

        else:
            print("Nevažeći odabir.")


def demo_test_mode(catalog):
    """Automatski pokreni demonstraciju testiranja."""
    print("\n=== DEMONSTRACIJA DCAT FUNKCIONALNOSTI ===")

    # 1. Sažetak kataloga
    print_catalog_summary(catalog)

    # 2. Pretraživanje skupova podataka
    test_dataset_search(catalog, "zdravstvo")
    test_dataset_search(catalog, "promet")

    # 3. Pretraživanje po formatu
    test_format_search(catalog, "CSV")
    test_format_search(catalog, "JSON")

    # 4. Vremensko pretraživanje
    test_temporal_search(catalog, 2023)

    # 5. Prostorno pretraživanje
    test_spatial_search(catalog, "Point")
    test_spatial_search(catalog, "Polygon")

    # 6. Servisi za skup podataka
    test_services_for_dataset(catalog, "dataset-edu-001")

    # 7. Povezani skupovi podataka
    test_related_datasets(catalog, "dataset-edu-001")


def main():
    """Glavna funkcija za pokretanje skripte za testiranje DCAT-a."""
    parser = argparse.ArgumentParser(
        description="Skripta za testiranje DCAT funkcionalnosti."
    )
    parser.add_argument(
        "--mode",
        choices=["interactive", "demo"],
        default="interactive",
        help="Način rada: interaktivni ili demo način (zadano: interactive)",
    )
    args = parser.parse_args()

    # Učitaj testni katalog
    catalog = load_test_catalog()

    # Pokreni odabrani način rada
    if args.mode == "interactive":
        interactive_test_mode(catalog)
    else:
        demo_test_mode(catalog)


if __name__ == "__main__":
    main()
