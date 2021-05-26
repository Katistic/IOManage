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
+ Loop runs in its own thread, so no asyncio management is required
```
