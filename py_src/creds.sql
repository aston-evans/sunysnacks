DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS locations;

INSERT INTO locations(name) VALUES('Argo Tea');
INSERT INTO locations(name) VALUES('Mills Marketplace');
INSERT INTO locations(name) VALUES('Mills Dining Hall');
INSERT INTO locations(name) VALUES('Seasons');
INSERT INTO locations(name) VALUES('Wilsbach Dining Hall');

CREATE TABLE user (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE locations (
  location_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL
);

CREATE TABLE reviews (
  review_id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  location_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,   
  title TEXT NOT NULL, 
  body TEXT NOT NULL,
  rating INTEGER NOT NULL
  FOREIGN KEY (author_id) REFERENCES user (user_id)
  FOREIGN KEY (location_id) REFERENCES locations (location_id)
);