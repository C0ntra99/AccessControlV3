from database import *
from tableDef import *

db = Database()

people = db.search({"name":"Toney, Brooklyn"})
for x in people:
    print("Person: ", x.name)
    print("ID: ", x.id)
    print("Email: ", x.email)
