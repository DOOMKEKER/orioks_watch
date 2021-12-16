create table users (
  tel_id VARCHAR(30) PRIMARY KEY NOT NULL,
  login VARCHAR(10) NOT NULL,
  password VARCHAR(50) NOT NULL
);
create table cm_s (
  tel_id VARCHAR(30) REFERENCES users(tel_id) NOT NULL,
  subject VARCHAR(100) NOT NULL,
  cm VARCHAR(50) NOT NULL,
  PRIMARY KEY (tel_id, subject, cm),
  ball FLOAT
);