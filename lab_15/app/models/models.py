from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Category(db.Model):
    """Категория блюда."""

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    dishes = db.relationship("Dish", back_populates="category", cascade="all, delete-orphan",
                             lazy="selectin")

    def __repr__(self):
        return f"Category({self.name!r})"


class Dish(db.Model):
    """Блюдо меню."""

    __tablename__ = "dishes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default="")
    price = db.Column(db.Float, nullable=False)
    calories = db.Column(db.Integer, nullable=False, default=0)
    available = db.Column(db.Boolean, nullable=False, default=True)

    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    category = db.relationship("Category", back_populates="dishes")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "calories": self.calories,
            "available": self.available,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
        }

    def __repr__(self):
        return f"Dish({self.name!r}, {self.price})"


order_items = db.Table(
    "order_items",
    db.Column("order_id", db.Integer, db.ForeignKey("orders.id"), primary_key=True),
    db.Column("dish_id", db.Integer, db.ForeignKey("dishes.id"), primary_key=True),
    db.Column("quantity", db.Integer, nullable=False, default=1),
)


class Order(db.Model):
    """Заказ: клиент + набор блюд (связь N:M через order_items)."""

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="принят")
    created_at = db.Column(db.String(20), nullable=False)

    dishes = db.relationship(
        "Dish", secondary=order_items, backref=db.backref("orders", lazy="dynamic"),
        lazy="selectin",
    )

    def total(self) -> float:
        return round(sum(dish.price for dish in self.dishes), 2)

    def quantities(self) -> dict:
        result = {}
        for dish in self.dishes:
            result[dish.id] = result.get(dish.id, 0) + 1
        return result

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "status": self.status,
            "created_at": self.created_at,
            "total": self.total(),
            "dish_ids": [dish.id for dish in self.dishes],
        }

    def __repr__(self):
        return f"Order({self.id}, {self.customer_name!r})"