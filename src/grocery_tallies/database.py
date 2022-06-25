import sqlalchemy.orm

from .constants import UNIT_REGISTRY

__all__ = [
    'Base',
    'Recipe',
    'Ingredient',
    'Store',
    'CategoryType',
    'Product',
    'UnitType',
]


Base = sqlalchemy.orm.declarative_base()


stores_products_table = sqlalchemy.Table(
    'stores_products',
    Base.metadata,
    sqlalchemy.Column('fk_store_id', sqlalchemy.ForeignKey('stores.id'), primary_key=True),
    sqlalchemy.Column('fk_product_id', sqlalchemy.ForeignKey('products.id'), primary_key=True),
    sqlalchemy.Column('location', sqlalchemy.String)
)


class Recipe(Base):
    __tablename__ = 'recipes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    source_url = sqlalchemy.Column(sqlalchemy.String)
    servings = sqlalchemy.Column(sqlalchemy.Integer, default=1)

    ingredients = sqlalchemy.orm.relationship('Ingredient', back_populates='recipe')


class Store(Base):
    __tablename__ = 'stores'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    address = sqlalchemy.Column(sqlalchemy.String)

    products = sqlalchemy.orm.relationship(
        'Product',
        secondary=stores_products_table,
        back_populates='stores'
    )


class CategoryType(Base):
    __tablename__ = 'category_types'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)

    products = sqlalchemy.orm.relationship('Product', back_populates='category')


class Product(Base):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)

    category_id = sqlalchemy.Column(
        'fk_category_type_id',
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey('category_types.id'),
        nullable=False,
    )
    category = sqlalchemy.orm.relationship('CategoryType', back_populates='products')

    ingredients = sqlalchemy.orm.relationship('Ingredient', back_populates='product')
    stores = sqlalchemy.orm.relationship(
        'Store',
        secondary=stores_products_table,
        back_populates='products'
    )

    def total_quantities(self):
        quantities = []
        for item in self.ingredients:
            item_qty = item.quantity * UNIT_REGISTRY(item.unit.name)
            for i, qty in enumerate(quantities):
                qty = item.quantity * UNIT_REGISTRY(item.unit.name)
                if not item.quantity.is_compatible_with(qty):
                    continue

                if item_qty.units > qty.units:
                    quantities[i] = item.quantity + qty
                else:
                    quantities[i] = qty + item.quantity
                break
            else:
                quantities.append(item_qty)

        return quantities


class UnitType(Base):
    __tablename__ = 'unit_types'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)

    ingredients = sqlalchemy.orm.relationship('Ingredient', back_populates='unit')


class Ingredient(Base):
    __tablename__ = 'ingredients'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    quantity = sqlalchemy.Column(sqlalchemy.Float, nullable=False)

    unit_id = sqlalchemy.Column(
        'fk_unit_type_id',
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey('unit_types.id'),
        nullable=False,
    )
    unit = sqlalchemy.orm.relationship('UnitType', back_populates='ingredients')

    recipe_id = sqlalchemy.Column(
        'fk_recipe_id',
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey('recipes.id'),
        nullable=False,
    )
    recipe = sqlalchemy.orm.relationship('Recipe', back_populates='ingredients')

    product_id = sqlalchemy.Column(
        'fk_product_id',
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey('products.id'),
        nullable=False,
    )
    product = sqlalchemy.orm.relationship('Product', back_populates='ingredients')
