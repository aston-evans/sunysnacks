--DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS locations;


/* Location tables */
CREATE TABLE Locations (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    latitude REAL,
    longitude REAL,
    map_url TEXT,
    image_filename TEXT
);

CREATE TABLE LocationHours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER NOT NULL,
    day_type TEXT NOT NULL,  -- 'weekdays', 'friday', 'saturday', 'sunday'
    hours TEXT NOT NULL,
    FOREIGN KEY(location_id) REFERENCES Location(location_id)
);

CREATE TABLE LocationLinks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER NOT NULL,
    link_type TEXT NOT NULL,  -- 'menu', 'instagram', 'android_app', 'ios_app'
    url TEXT NOT NULL,
    FOREIGN KEY(location_id) REFERENCES Locations(location_id)
);

CREATE TABLE Reviews (
  review_id INTEGER PRIMARY KEY AUTOINCREMENT,
  --author_id INTEGER NOT NULL,
  location_id INTEGER NOT NULL,
  --created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL, 
  body TEXT NOT NULL,
  rating INTEGER NOT NULL,
  --FOREIGN KEY (author_id) REFERENCES user (user_id)
  nickname TEXT NOT NULL,
  FOREIGN KEY (location_id) REFERENCES Locations (location_id)
);