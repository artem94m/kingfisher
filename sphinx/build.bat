@echo off

set docs_folder="..\docs"

rem delete old data
if exist %docs_folder% rd /q /s %docs_folder%

rem build html
call sphinx-build -b html . %docs_folder%

rem create file for GitHub Pages
call type nul > "..\docs\.nojekyll"
