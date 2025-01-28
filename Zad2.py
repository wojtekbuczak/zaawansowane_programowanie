from Student import Student
from Library import Library
from Employee import Employee
from Book import Book
from Order import Order


student1 = Student("Jan Kowalski", [60, 70, 80])
student2 = Student("Piotr Nowak", [40, 45, 50])

# Biblioteki
library1 = Library("New York", "5th Avenue", "10001", "9 AM - 5 PM", "123-456-789")
library2 = Library("Los Angeles", "Sunset Blvd", "90001", "10 AM - 6 PM", "987-654-321")

# Książki
book1 = Book(library1, "2020-01-01", "George", "Orwell", 328)
book2 = Book(library1, "2021-05-15", "Aldous", "Huxley", 288)
book3 = Book(library2, "2019-11-22", "J.K.", "Rowling", 400)
book4 = Book(library2, "2018-07-19", "Tolkien", "J.R.R.", 310)
book5 = Book(library1, "2017-03-10", "Mark", "Twain", 200)

# Pracownicy
employee1 = Employee(
    "Alice",
    "Johnson",
    "2015-06-01",
    "1985-09-15",
    "New York",
    "5th Avenue",
    "10001",
    "123-456-789",
)
employee2 = Employee(
    "Bob",
    "Williams",
    "2018-08-12",
    "1990-04-20",
    "Los Angeles",
    "Sunset Blvd",
    "90001",
    "987-654-321",
)
employee3 = Employee(
    "Charlie",
    "Brown",
    "2020-03-05",
    "1995-12-25",
    "New York",
    "5th Avenue",
    "10001",
    "123-456-789",
)

# Zamówienia
order1 = Order(employee1, student1, [book1, book2], "2023-12-01")
order2 = Order(employee2, student2, [book3, book4, book5], "2024-01-15")

# Wyświetlenie zamówień
print(order1)
print(order2)
