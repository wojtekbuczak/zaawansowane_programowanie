from flask import Flask
from flask_restful import Resource, Api
import csv

# Inicjalizacja aplikacji Flask
app = Flask(__name__)
api = Api(app)

# Klasa Movie - model danych
class Movie:
    def __init__(self, movieId, title, genres):
        self.movieId = movieId
        self.title = title
        self.genres = genres

    def __repr__(self):
        return f"<Movie {self.movieId}>"

# Klasa obsługująca endpoint /movies
class MoviesList(Resource):
    def get(self):
        movies = []

        # Pobranie danych z pliku CSV
        try:
            with open('movies.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Tworzenie obiektu Movie na podstawie wiersza
                    movie = Movie(row['movieId'], row['title'], row['genres'])
                    # Serializacja obiektu przy użyciu __dict__
                    movies.append(movie.__dict__)
        except FileNotFoundError:
            return {"error": "File not found"}, 404

        # Zwracanie listy zserializowanych obiektów
        return movies, 200

# Rejestracja endpointu
api.add_resource(MoviesList, '/movies')

if __name__ == '__main__':
    app.run(debug=True)
