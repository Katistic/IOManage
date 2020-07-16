from iomanage.ioerror import *
import os

class IODict:
    def _can_int(self, string):
        try:
            int(string)
            return True
        except:
            return False

    def _encoding(self, string):
        encodes = {
            "true": True,
            "false": False,
            "null": None
        }

        if string in encodes: return encodes[string]
        elif self._can_int(string): return int(string)
        elif type(string) == str: return string[1:len(string)-1]
        return string

    def __getitem__(self, key):
        if type(key) != str: raise TypeError("IODict indices must be strings, not " + str(type(key)))

        with open(self.file, "r") as tfile:
            tfile.seek(0, 2)

            size = tfile.tell()
            keymatch = ""
            data = ""
            dataseek = 0
            inquotes = False
            secondlast = ""

            tfile.seek(self.sbyte)
            while keymatch != key and tfile.tell() != size:
                # Get key
                keymatch = ""
                c = tfile.read(1)

                while not (inquotes == False and c == ":"):
                    secondlast = c
                    c = tfile.read(1)

                    if c == "\"" and secondlast != "\\":
                        inquotes = not inquotes
                    elif inquotes:
                        keymatch += c

                # Check if key is correct
                dataseek = tfile.tell()
                if key == keymatch: break

                # Go to next key
                while not (inquotes == False and c == ",") and tfile.tell() != size:
                    c = tfile.read(1)

                    if c == "\"" and secondlast != "\\":
                        inquotes = not inquotes

            # Get key data if key is found
            if keymatch == key:
                tfile.seek(dataseek)

                while not (inquotes == False and (c == "," or c == "}")):
                    secondlast = c
                    c = tfile.read(1)

                    if data == "" and not inquotes:
                        if c == "{": return IODict(tfile.tell() - 1, self.parent)
                        elif c == "[": return IOList(tfile.tell() - 1, self.parent)

                    if c == "\"" and secondlast != "\\":
                        inquotes = not inquotes
                    if not inquotes and c in " }\n,": continue

                    data += c

                return self._encoding(data)
            else: # Or don't
                raise KeyError(key)

    def __iter__(self):
        pass

    def __next__(self):
        pass

    def __init__(self, sbyte, parent=None, file=None):
        self.parent = parent
        self.sbyte = sbyte
        self.__lastv = None

        if parent != None:
            self.file = self.parent.file
        elif file != None and not os.path.isfile(file):
            raise MissingFileError("File not found: " + os.path.abspath(file))
        else:
            raise RequiredParamError("One of 'parent' or 'file' kwargs must be passed")

class IOList(IODict):
    def __getitem__(self, key):
        if type(key) != int: raise TypeError("IOList indices must be integers, not " + str(type(key)))

        size = len(self) - 1

        if size == -1: raise IndexError("IOList index out of range")
        elif key < 0 and key * - 1 - 1 > size: raise IndexError("IOList index out of range")
        elif key > 0 and key > size: raise IndexError("IOList index out of range")

        index = -1

        for item in self:
            index += 1
            if index == key: return item

    def __iter__(self):
        self.lbyte = self.sbyte
        self.lfinish = False
        return self

    def __next__(self):
        if self.lfinish:
            self.lfinish = False
            raise StopIteration

        with open(self.file, "r") as tfile:
            tfile.seek(self.lbyte)

            c = tfile.read(1)
            secondlast = ""
            inquotes = False
            brackets = 0

            data = ""
            datacomplete = False

            while not datacomplete:
                secondlast = c
                c = tfile.read(1)
                self.lbyte = tfile.tell() - 1

                if data == "" and not inquotes:
                    if c == "{": return IODict(tfile.tell() - 1, self.parent)
                    elif c == "[": return IOList(tfile.tell() - 1, self.parent)

                if c == "\"" and secondlast != "\\": inquotes = not inquotes
                if not inquotes:
                    if c == " ": continue
                    elif c == ",":
                        datacomplete = True
                        continue
                    elif c == "]":
                        self.lfinish = True
                        datacomplete = True
                        continue

                data += c

            return self._encoding(data)

    def __len__(self):
        length = 0

        for item in self:
            length += 1

        return length

    def __init__(self, sbyte, parent=None, file=None):
        super().__init__(sbyte, parent, file)

        self.lbyte = self.sbyte
        self.lfinish = False

class IOJson(IODict):
    def __init__(self, file):
        if os.path.isfile(file):
            self.file = file
        else:
            raise MissingFileError("File not found: " + os.path.abspath(file))

        super().__init__(0, self)
