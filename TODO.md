## TODO
- Refactor core.py: 
    * split it into submodules
    * make it compliant to flake8
- Make logger global and reachable through getLogger()
- Add init actions:
    * "check" the checks: if they were OK - use hash to check if they are still the same
    * delete logs which are older than "store_logs_for" param in config.py
- Unit tests + coverage module
- Sphinx docs: 
    * do not generate docs for all the source code, but collect all the README.md
    * use Github Pages to host generated html pages
- Store parsed checks in memory (global_storage.py)
- Add multiprocessing to the kingfisher.py for scanning different files in parallel
