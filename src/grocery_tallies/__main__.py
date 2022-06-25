import json
import os.path
import pprint
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from PySide2 import QtWidgets

import grocery_tallies
# from grocery_tallies import GroceryTallies


from sqlalchemy.ext.declarative import DeclarativeMeta


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                if isinstance(data, list):
                    continue

                try:
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    continue
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)


engine = create_engine('sqlite:///:memory:', echo=False)
grocery_tallies.Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

with open('./src/json/unit_types.json', 'r') as f:
    json_data = json.load(f)
    for data in json_data:
        session.add(grocery_tallies.UnitType(**data))

with open('./src/json/category_types.json', 'r') as f:
    json_data = json.load(f)
    for data in json_data:
        session.add(grocery_tallies.CategoryType(**data))

session.commit()


produce = session.query(grocery_tallies.CategoryType).filter(grocery_tallies.CategoryType.name == 'Produce').one()
dairy = session.query(grocery_tallies.CategoryType).filter(grocery_tallies.CategoryType.name == 'Dairy').one()
dry_goods = session.query(grocery_tallies.CategoryType).filter(grocery_tallies.CategoryType.name == 'Dry Goods').one()
canned_goods = session.query(grocery_tallies.CategoryType).filter(grocery_tallies.CategoryType.name == 'Canned Goods').one()
products = [
    grocery_tallies.Product(name='Roma Tomatoes', category=produce),
    grocery_tallies.Product(name='Cucumber', category=produce),
    grocery_tallies.Product(name='Onion', category=produce),
    grocery_tallies.Product(name='Red Bell Pepper', category=produce),
    grocery_tallies.Product(name='Garlic Clove', category=produce),

    grocery_tallies.Product(name='Milk', category=dairy),
    grocery_tallies.Product(name='Shredded Cheese', category=dairy),
    grocery_tallies.Product(name='Sliced Cheese', category=dairy),
    grocery_tallies.Product(name='Eggs', category=dairy),
    grocery_tallies.Product(name='Yogurt', category=dairy),
    grocery_tallies.Product(name='Butter', category=dairy),

    grocery_tallies.Product(name='Bread', category=dry_goods),
    grocery_tallies.Product(name='Flour', category=dry_goods),
    grocery_tallies.Product(name='Sugar', category=dry_goods),

    grocery_tallies.Product(name='Black Beans', category=canned_goods),
    grocery_tallies.Product(name='Pinto Beans', category=canned_goods),
    grocery_tallies.Product(name='Green Beans', category=canned_goods),
    grocery_tallies.Product(name='Diced Tomatoes', category=canned_goods),
]

for x in products:
    session.add(x)

session.commit()

results = []
for x in products:
    results.append(x)

with open('./src/json/products.json', 'w') as f:
    json.dump(results, f, indent=2, cls=AlchemyEncoder)

# app = QtWidgets.QApplication(sys.argv)
# widget = GroceryTallies()
# sys.exit(widget.exec_())
sys.exit(0)
