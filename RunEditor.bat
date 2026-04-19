@echo off
set pyexe=py -3
if NOT [%1]==[] (
%pyexe% MME_NDS.py -R %1
) else (
%pyexe% MME_NDS.py
)
