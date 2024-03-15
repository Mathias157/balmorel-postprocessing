# Excel-Python Tool for Balmorel Post-Processing 

"InteractiveResults.xlsm" is the excel interface for processing Balmorel results. 
Python scripts perform most of the data processing, which ensures a more efficient excel experience - at least while no unexpected errors are encountered.  

The first sheet contains an installation manual and a guide.

Follow the guide to ensure that all paths are correct and the excel functions properly.

NOTE: 
- The VBA and excel coding currently assumes a Windows operating system
- Paths get screwed up if putting this in a OneDrive synchronised folder. So, do either of the following:
  - Place the repo in a folder not synchronised by OneDrive, e.g. C:\Users\\%your_user_name%
  - Hardcode the path in cell B8 of the ExcelPathCommands sheet 
