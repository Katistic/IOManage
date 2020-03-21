# IOManage
 Manages IO operations of a single file

## Applications in which this library is useful

The only scenario I made this library for is when reading and
writing from a single file in more than a single thread.

## Features

```diff
+ Read/Write queue system
+ Can cleanly close file, finishing all r/w functions before terminating
+ ID system for holding queue for write after a read to prevent data mismatching
+ Loop runs in its own thread, so no asyncio management is required
```
