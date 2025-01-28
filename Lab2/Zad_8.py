import requests
from typing import Optional, List
import argparse


class Brewery:
    def __init__(
        self,
        id: str,
        name: str,
        brewery_type: str,
        street: Optional[str],
        city: str,
        state: str,
        postal_code: str,
        country: str,
        longitude: Optional[float],
        latitude: Optional[float],
        phone: Optional[str],
        website_url: Optional[str],
    ):
        self.id = id
        self.name = name
        self.brewery_type = brewery_type
        self.street = street
        self.city = city
        self.state = state
        self.postal_code = postal_code
        self.country = country
        self.longitude = longitude
        self.latitude = latitude
        self.phone = phone
        self.website_url = website_url

    def __str__(self):
        return (
            f"Brewery ID: {self.id}\n"
            f"Name: {self.name}\n"
            f"Type: {self.brewery_type}\n"
            f"Address: {self.street or 'N/A'}, {self.city}, {self.state}, {self.postal_code}, {self.country}\n"
            f"Coordinates: ({self.latitude or 'N/A'}, {self.longitude or 'N/A'})\n"
            f"Phone: {self.phone or 'N/A'}\n"
            f"Website: {self.website_url or 'N/A'}\n"
        )


def fetch_breweries(city: Optional[str] = None) -> List[Brewery]:
    url = "https://api.openbrewerydb.org/v1/breweries"
    params = {"per_page": 20}

    if city:
        params["by_city"] = city

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        breweries = []
        for item in data:
            brewery = Brewery(
                id=item.get("id"),
                name=item.get("name"),
                brewery_type=item.get("brewery_type"),
                street=item.get("street"),
                city=item.get("city"),
                state=item.get("state"),
                postal_code=item.get("postal_code"),
                country=item.get("country"),
                longitude=float(item["longitude"]) if item.get("longitude") else None,
                latitude=float(item["latitude"]) if item.get("latitude") else None,
                phone=item.get("phone"),
                website_url=item.get("website_url"),
            )
            breweries.append(brewery)

        return breweries

    except requests.RequestException as e:
        print(f"Error fetching breweries: {e}")
        return []


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch breweries information.")
    parser.add_argument(
        "--city", type=str, help="Filter breweries by city.", required=False
    )
    args = parser.parse_args()

    breweries = fetch_breweries(city=args.city)

    for brewery in breweries:
        print(brewery)
        print("-" * 40)
