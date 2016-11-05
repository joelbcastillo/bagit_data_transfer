set tdate=%date: =%
set tdate=%tdate:/=%
set ttime=%time::=%
set ttime=%ttime:.=%
set ttime=%ttime: =%
robocopy "SOURCE" "DESTINATION" /W:0 /TEE /e /V /LOG:C:\LOGDIR_PATH\Public_%tdate%-%ttime%.log /R:1 /ZB /COPYALL /np
