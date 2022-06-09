from ZachsStupidImageLibrary.coolstuff import textimage
import hashlib
import sqlite3
import time
import re
import ImageCommands.queries as queries

class Commander:
    def __init__(self, savepath="imagecommands.db"):
        self.savepath = savepath
        self.opendb()

    def __del__(self):
        self.closedb()

    def opendb(self):
        self.con = sqlite3.connect(self.savepath)
        self.cursor = self.con.cursor()
        # Ensure the table exists
        self.cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='imagecommands'")
        if self.cursor.fetchone()[0] != 1:
            self.cursor.executescript(queries.createdb)

    def closedb(self):
        try:
            self.con.commit()
            self.con.close()
        except sqlite3.ProgrammingError:
            pass

    # Remove this after a commit
    def executescriptfromfile(self, filename):
        with open(filename, 'r') as f:
            script = f.read()

        self.cursor.executescript(script)
        self.con.commit()

    def spawngoon(self, command, img=None, text=None):
        return Goon(self, command=command)

class Goon:
    def __init__(self, commander, commandhash=None, command=None, imagesavedat=None):
        def setupfromcommandhash():
            self.commander.cursor.execute("""SELECT command FROM imagecommands WHERE commandhash=? """,
                                          (self.commandhash,))
            results = self.commander.cursor.fetchall()
            if len(results) == 0:
                raise Exception(f"That commandhash({self.commandhash}) doesn't freaking exist!!!!")
            self.command = results[0][0]

        def setupfromcommand():
            # Get the hash
            self.commandhash = hashlib.md5(self.command.encode('utf-8')).hexdigest()
            # Add the command
            self.commander.cursor.execute("""SELECT commandhash, command FROM imagecommands WHERE commandhash=? """,
                                          (self.commandhash, ) )
            results = self.commander.cursor.fetchall()
            if len(results) == 0:
                self.commander.cursor.execute(f"""INSERT INTO imagecommands(commandhash, command) VALUES(?, ?)""",
                                 (self.commandhash, self.command))
                self.updatelastinteraction()
            elif results[0][1] != self.command:
                raise Exception("Two distinct commands have the same hash. What are the odds, right?")
            else:
                self.updatelastinteraction()

        def setupfromimagesavedat():
            match = re.search(r"{([a-z0-9]{32})\}", self.imagesavedat)
            if match is None:
                raise Exception(f"'{self.imagesavedat}' doesn't have a hash in it for me to use.")
            self.commandhash = match.group(1)
            setupfromcommandhash()

        self.commander = commander
        self.commandhash = commandhash
        self.command = command
        self.imagesavedat = imagesavedat

        if self.command is not None:
            setupfromcommand()
        elif self.commandhash is not None:
            setupfromcommandhash()
        elif self.imagesavedat is not None:
            setupfromimagesavedat()

    def act(self):
        exec(self.command)
        self.updatelastinteraction()

    def saveimage(self, imagesavepath, img=None, text=None):
        # Generate an image if one isn't provided
        if not img:
            if not text:
                text = self.command
            img = textimage(text)

        # Save the image
        # The hash would be saved in the metadata, but it turns out windows metadata SUCKS and you can't make custom fields
        if imagesavepath.count("{}") != 1:
            raise Exception("imagesavepath needs exactly one {} for me to throw the hash into")
        imagesavepath = imagesavepath.replace("{}", "{"+self.commandhash+"}")
        img.save(imagesavepath)
        self.imagesavedat = imagesavepath

    def updatelastinteraction(self):
        self.commander.cursor.execute("""UPDATE imagecommands SET lastinteraction = ? WHERE commandhash = ?""",
                         (time.time(), self.commandhash))

commander = Commander()
goon = commander.spawngoon('print("LOL")')
goon.saveimage("test {}.png")
goon.act()