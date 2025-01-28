import requests
from typing import Optional, List


class Brewery:
    def __init__(
        self,
        id: str,
        name: str,
        brewery_type: str,
        address_1: str,
        address_2: str,
        address_3: str,
        city: str,
        state_province: str,
        postal_code: str,
        country: str,
        longitude: float,
        latitude: float,
        phone: str,
        website_url: str,
        state: str,
        street: str,
    ):
        self.id = id
        self.name = name
        self.brewery_type = brewery_type
        self.address_1 = (address_1,)
        self.address_2 = (address_2,)
        self.address_3 = (address_3,)
        self.city = city
        self.state_province = (state_province,)
        self.postal_code = postal_code
        self.country = country
        self.longitude = longitude
        self.latitude = latitude
        self.phone = phone
        self.website_url = website_url
        self.state = state
        self.street = street

    def __str__(self):
        return (
            f"Brewery ID: {self.id}\n"
            f"Name: {self.name}\n"
            f"Type: {self.brewery_type}\n"
            f"Address: {self.address_1}, {self.address_2}, {self.address_3}, {self.street or 'N/A'}, {self.city}, {self.state_province} {self.state}, {self.postal_code}, {self.country}\n"
            f"Coordinates: ({self.latitude or 'N/A'}, {self.longitude or 'N/A'})\n"
            f"Phone: {self.phone or 'N/A'}\n"
            f"Website: {self.website_url or 'N/A'}\n"
        )


def fetch_breweries() -> List[Brewery]:
    url = "https://api.openbrewerydb.org/v1/breweries"
    params = {"per_page": 20}

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
                address_1=item.get("address_1"),
                address_2=item.get("address_2"),
                address_3=item.get("address_3"),
                city=item.get("city"),
                state_province=item.get("state_province"),
                postal_code=item.get("postal_code"),
                country=item.get("country"),
                longitude=float(item["longitude"]) if item.get("longitude") else None,
                latitude=float(item["latitude"]) if item.get("latitude") else None,
                phone=item.get("phone"),
                website_url=item.get("website_url"),
                state=item.get("state"),
                street=item.get("street"),
            )
            breweries.append(brewery)

        return breweries

    except requests.RequestException as e:
        print(f"Error fetching breweries: {e}")
        return []


if __name__ == "__main__":
    breweries = fetch_breweries()

    for brewery in breweries:
        print(brewery)
        print("-" * 40)
