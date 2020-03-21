import threading
import time
import uuid
import json
import os

class IOManager: ## Manages reading and writing data to files.
    def __init__(self, file, start=True, jtype=True, binary=False):
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
        '''

        self.Ops = [] # Operations
        self.Out = {} # Outputs
        self.Reserved = [] # Reserved keys for operations

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
            self.Start()

    def GetId(self): # Class to get a probably unique key
        return uuid.uuid4()

    def Read(self, waitforwrite=False, id=None): # Handles creating read operations
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

    def Write(self, nd, id=None):
        '''
        nd:
            type, string/bytes
            New data to write to file
        id:
            -- OPTIONAL --
            type, uuid
            default, None
            ID to identify this operation
        '''

        self.Ops.append({"type": "w", "d": nd, "id": id}) # Add write operation to list

    def Start(self): # Start operations thread
        if self.stopped: # Start only if thread not running
            self.stopthread = False # Reset stopthread to avoid immediate stoppage

            # Create thread and start
            self.thread = threading.Thread(target=self.ThreadFunc)
            self.thread.start()

    def Stop(self): # Stop operations thread
        if not self.stopthread: # Stop thread only if not already stopping
            if not self.stopped: # Stop thread only if thread running
                self.stopthread = True

    def isStopped(self): # Test if operations thread not running
        return self.stopped

    def ThreadFunc(self): # Operations function
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

            else: # If no operations, wait.
                time.sleep(.1)

        self.stopped = True # Set operation thread as stopped
