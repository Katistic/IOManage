# IOManage
 Manages IO operations of a single file

## Applications in which this library is useful

The only scenario I made this library for is when reading and
writing from a single file in more than a single thread.

Currently also working on classes to read and write from/to massive JSON files

## Features

```diff
! IOManager Class
+ Read/Write queue system
+ Can cleanly close file, finishing all r/w functions before terminating
+ ID system for holding queue for write after a read to prevent data mismatching
+ Loop runs in its own thread, so no asyncio management is required

! IOJson, IOList and IODict Classes
+ Can index massive lists and dicts from JSON files
+ Dictionaries read from JSON are IODict objects
+ Lists read from JSON are IOList objects
+ Each IOList, IODict, and IOJson class has only 1 key and/or value stored in memory at one time
- Can not detect malformed JSON, instead will (probably) break
- Can not (yet) iterate through IODict, and IOJson classes
- NOT THREADSAFE!
```
