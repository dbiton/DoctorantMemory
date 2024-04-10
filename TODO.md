# To Do

- [ ] Add option for ignoring instruction fetch (IF) memory accesses in parse
- [ ] Add option to use bytes or cache lines
- [ ] Add to memory_accesses tool a header containing the following:
    - [ ] Address space
    - [ ] Percentage reads and writes in bytes (account for request size)
- [ ] Add option in memory_accesses to split reads & writes into line sized requests
- [ ] Add option for not writing app output to file
- [ ] Implement our own tools instead of drcachesim's ones to be more robust
    - [ ] Write memory_accesses output to file, use linux's sort, unique etc