# A less-ugly place to store larger/more important executions.

createdb = """
CREATE TABLE imagecommands (
    commandhash     TEXT    NOT NULL    PRIMARY KEY,
    command         TEXT    NOT NULL,
    lastinteraction INTEGER
)
"""

def lol():
    pass