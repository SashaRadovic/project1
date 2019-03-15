import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
os.environ["DATABASE_URL"]="postgres://wimnopegmrmjwv:8ae4461cdeba46d5967ea37063c1b85d659262f11c2b59b2865b1b31652b999e@ec2-79-125-4-96.eu-west-1.compute.amazonaws.com:5432/d45tl12lu17jti"
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
db.execute("CREATE TABLE books(id SERIAL, isbn VARCHAR PRIMARY KEY NOT NULL, title VARCHAR NOT NULL, author VARCHAR, year varchar(4) )")
def main():

    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                   {"isbn": isbn, "title": title, "author": author, "year": year})

    db.commit()

if __name__ == "__main__":
    main()
