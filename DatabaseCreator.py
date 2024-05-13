from cs50 import SQL
from datetime import datetime

date = datetime.now()

db = SQL("sqlite:///database/database.db")

#db.execute("DROP TABLE jump")
#db.execute("DROP TABLE training")
#db.execute("DROP TABLE skater")

#db.execute(
"""CREATE TABLE skater (
                skater_id INTEGER NOT NULL,
                skater_name VARCHAR,
                CONSTRAINT skater_id PRIMARY KEY (skater_id)
);"""
#)

#db.execute(
"""CREATE TABLE training (
                training_id INTEGER NOT NULL,
                skater_id INTEGER NOT NULL,
                training_date DATE NOT NULL,
                CONSTRAINT training_id PRIMARY KEY (training_id)
                FOREIGN KEY(skater_id) REFERENCES skater(skater_id) ON DELETE CASCADE
);"""
#)

#db.execute(
"""CREATE TABLE jump (
                jump_id INTEGER NOT NULL,
                training_id INTEGER NOT NULL,
                jump_type INTEGER NOT NULL,
                jump_rotations FLOAT NOT NULL,
                jump_success BOOLEAN NOT NULL,
                jump_time INTEGER NOT NULL,
                CONSTRAINT jump_id PRIMARY KEY (jump_id)
                FOREIGN KEY(training_id) REFERENCES training(training_id) ON DELETE CASCADE
);"""
#)