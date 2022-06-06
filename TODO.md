## TODO
- Refactor core.py: 
    * split it into submodules
    * make it compliant to flake8
- Make logger global and reachable through getLogger()
- Add init actions:
    * "check" checks: if they were OK - use hash to check if they are still the same
- unit tests
- sphinx
- store parsed checks in memory (global_storage.py)
- Add multiprocessing to the kingfisher.py for scanning different files in parallel
