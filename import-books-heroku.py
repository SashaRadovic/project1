import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
os.environ["DATABASE_URL"]="DATABASE_URL"
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
db.execute("CREATE TABLE books(id SERIAL, isbn VARCHAR PRIMARY KEY NOT NULL, title VARCHAR NOT NULL, author VARCHAR, year varchar(4) )")
def main():

    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                   {"isbn": isbn, "title": title, "author": author, "year": year})
    print("executed!")
    db.commit()

if __name__ == "__main__":
    main()
