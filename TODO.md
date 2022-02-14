## TODO
1. Refactor core.py: 
    * split it into submodules
    * make it compliant to flake8
2. Make logger global and reachable through getLogger()
3. Add init actions:
    * "check" checks: if they were OK - use hash to check if they are still the same
4. Add multiprocessing to the kingfisher.py for scanning different files in parallel
