from database import Base,engine
from models import Product,Sale

print("Creating database ....")
Base.metadata.create_all(engine)