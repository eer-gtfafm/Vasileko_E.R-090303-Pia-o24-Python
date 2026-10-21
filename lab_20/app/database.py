from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Dish(db.Model):
    """Блюдо ресторана."""

    __tablename__ = "dishes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "price": self.price}


def init_db() -> None:
    db.create_all()
    if Dish.query.count() == 0:
        db.session.add_all([
            Dish(name="Борщ", price=350.0),
            Dish(name="Цезарь", price=420.0),
            Dish(name="Стейк", price=890.0),
            Dish(name="Паста", price=450.0),
            Dish(name="Чизкейк", price=320.0),
        ])
        db.session.commit()