import threading
import time
import uuid
import json
import os

class IOManager: ## Manages reading and writing data to files.
    def __init__(self, file, start=True, jtype=True, binary=False, old=False):
        '''
        file:
            type, string
            Path to file to iomanage
        start:
            -- OPTIONAL --
            type, boolean
            default, True
            Start operations thread on creation
        jtype:
            -- OPTIONAL --
            type, boolean
            default, True
            File is json database
        binary:
            -- OPTIONAL --
            type, boolean
            default, False
            Open file in binary read/write mode
        old:
            -- OPTIONAL --
            type, boolean
            default, False
            Use old read/write operation manager
        '''

        self.Ops = [] # Operations
        self.Out = {} # Outputs
        self.Reserved = [] # Reserved keys for operations

        self.useOldOpManager = old
        self.stopthread = False # Should stop operations thread
        self.stopped = True # Is operations thread stopped
        self.thread = None # Operation thread object
        self.file = file # File to read/write

        ## Assigning open params to class

        if binary: # Can not be json type and binary read/write
            self.jtype = False
        else:
            self.jtype = jtype

        self.binary = binary

        # Create file if it doesn't already exist
        if not os.path.isfile(file):
            with open(file, "w+") as file:
                if jtype:
                    file.write("{}")

        if start: # start if kwarg start is True
            self.start()

    def getId(self): # Get a probably unique key
        return uuid.uuid4()

    def read(self, waitforwrite=False, id=None): # Handles creating read operations
        '''
        waitforwrite:
            -- OPTIONAL --
            type, boolean
            default, False
            Operations thread should wait for write process same id kwarg
            Requires id kwarg to be set
        id:
            -- OPTIONAL --
            type, uuid4
            default, None
            ID to identify this operation
        '''

        if not waitforwrite:
            if id == None: id = uuid.uuid4() # get uuid if none passed
            self.Ops.append({"type": "r", "wfw": False, "id": id}) # Add operation to list
        else: # Wait for next write with same id
            if id == None: # waitforwrite requires id
                return None

            # Check for duplicate ids

            for x in self.Ops:
                if x["id"] == id:
                    return None

            if id in self.Reserved:
                return None

            # Reserve id
            # Add operation to list
            self.Reserved.append(id)
            self.Ops.append({"type": "r", "wfw": True, "id": id})

        while not id in self.Out: # Wait for read operation to complete
            time.sleep(.01)

        result = self.Out[id] # Get results
        del self.Out[id] # Delete results from output
        return result["data"] # return results

    def write(self, nd, id=None):
        '''
        nd:
            type, dictionary
            New data to write to file
        id:
            -- OPTIONAL --
            type, uuid
            default, None
            ID to identify this operation
        '''

        if id == None: id = uuid.uuid4() # Get ID if none given
        self.Ops.append({"type": "w", "d": nd, "id": id}) # Add write operation to list

        while not id in self.Out: # Wait for operation to finish
            time.sleep(0.01)

        del self.Out[id] # Remove operation data
        return

    def start(self): # Start operations thread
        if self.stopped: # Start only if thread not running
            self.stopthread = False # Reset stopthread to avoid immediate stoppage

            # Create thread and start
            if self.useOldOpManager:
                self.thread = threading.Thread(target=self.oThreadFunc)
            else:
                self.thread = threading.Thread(target=self.threadFunc)
            self.thread.start()

    def stop(self): # Stop operations thread
        if not self.stopthread: # Stop thread only if not already stopping
            if not self.stopped: # Stop thread only if thread running
                self.stopthread = True

    def isStopped(self): # Test if operations thread not running
        return self.stopped

    def doOperation(self, file, Next):
        id = Next["id"] # Operation ID

        if Next["type"] == "r": # If is read operation

            # Use json.load if in json mode
            if self.jtype:
                d = json.load(file)
            else:
                d = file.read()

            # Put data in output
            self.Out[id] = {"data": d, "id": id}

            if Next["wfw"]: # Test if read operation is wait-for-write
                 # Wait for write loop
                while not self.stopthread: # Test for stop attr

                    # Search for write operation with same id
                    op = None
                    for op in self.Ops:
                        if op["id"] == id:
                            break

                    # If no write operation, wait and restart loop
                    if op == None:
                        time.sleep(.1)
                        return

                    self.Reserved.remove(id) # Remove reserved id
                    self.Ops.remove(op) # Remove write operation from list
                    self.Ops.insert(0, op) # Place write operation first
                    return

        elif Next["type"] == "w": # If is write operation

            # Use json.dump if in json mode
            if self.jtype:
                json.dump(Next["d"], file, indent=4)
            else:
                file.write(Next["d"])

            # Put data in output
            self.Out[id] = {"id": id}

    def threadFunc(self): # Operations Function
        self.stopped = False # Reset stopped attribute

        # File attributes
        if self.binary:
            t = "b"
        else:
            t = ""

        lOp = "" # Last operation type
        oFile = None # Opened File

        # Operation Loop
        while not self.stopthread: # While thread not being told to halt
            # Get next operation
            if len(self.Ops) > 0: # If there is an operation queued
                # Get next operation
                Next = self.Ops[0]
                del self.Ops[0]

                if Next["type"] == lOp: # If operation is same type as last operation
                    oFile.seek(0) # Seek to start of file
                    self.doOperation(oFile, Next) # Do the operation
                else:
                    lOp = Next["type"]
                    if not oFile == None: oFile.close()
                    oFile = open(self.file, lOp+t) # Open file
                    self.doOperation(oFile, Next) # Do the operation
            else:
                time.sleep(.1)

        self.stopped = True # Set operation thread as stopped

    def oThreadFunc(self): # Old Operations function
        self.stopped = False # Reset stopped attr

        # Read/write type, binary or not
        t = None
        if self.binary:
            t = "b"
        else:
            t = ""

        # Main loop
        while not self.stopthread: # Test for stop attr
            if len(self.Ops) > 0: # Test for new operations

                # Get next operation
                Next = self.Ops[0]
                del self.Ops[0]

                # Open file as 'type' (read/write) + t (binary/text)
                with open(self.file, Next["type"]+t) as file:
                    id = Next["id"] # Operation ID

                    if Next["type"] == "r": # If is read operation

                        # Use json.load if in json mode
                        if self.jtype:
                            d = json.load(file)
                        else:
                            d = file.read()

                        # Put data in output
                        self.Out[id] = {"data": d, "id": id}

                        if Next["wfw"]: # Test if read operation is wait-for-write
                             # Wait for write loop
                            while not self.stopthread: # Test for stop attr

                                # Search for write operation with same id
                                op = None
                                for op in self.Ops:
                                    if op["id"] == id:
                                        break

                                # If no write operation, wait and restart loop
                                if op == None:
                                    time.sleep(.1)
                                    continue

                                self.Reserved.remove(id) # Remove reserved id
                                self.Ops.remove(op) # Remove write operation from list
                                self.Ops.insert(0, op) # Place write operation first
                                break # Break wfw loop
                            continue # Continue to main loop start

                    elif Next["type"] == "w": # If is write operation

                        # Use json.dump if in json mode
                        if self.jtype:
                            json.dump(Next["d"], file, indent=4)
                        else:
                            file.write(Next["d"])

                        self.Out[id] = {"id": id}

            else: # If no operations, wait.
                time.sleep(.1)

        self.stopped = True # Set operation thread as stopped
