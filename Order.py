class Order:
    def __init__(self, employee, student, books, order_date):
        self.employee = employee
        self.student = student
        self.books = books
        self.order_date = order_date

    def __str__(self):
        books_str = ", ".join(str(book) for book in self.books)
        return (
            f"Order(employee={self.employee}, student={self.student}, "
            f"books=[{books_str}], order_date={self.order_date})"
        )
