# Loading Table(s) - Guide

## Reference: cFE User's Guide
Reference URL: https://github.com/nasa/cFS/blob/gh-pages/cFE_Users_Guide.pdf

1. Make sure the table image you want to load is in the on-board computer. 
1. Open Your GroundSystem. 
    1. Select "Start Command System".
    1. Select "Display Page" next to Table Services. This will take you to "Table Services" menu.
    1. Select "Send" next to "CFE_TBL_LOAD_CC". 
    1. Enter the location and name of the table file you want to load in the input section:
    
        Example: `/cf/MyTblDefault2.tbl`
    
    1. Select "send". If successful, you should see an event:
    
        `"Successful load of '/cf/<Your_Table_File_Name>' into '<Your_APP>.<Your_Table_Name>' work buffer"`

    1. At this point, your table is loaded but still "inactive". Before you can "activate" the table, you will have to "validate" it. Go back to "Table Services" menu.
    1. Select "Send" next to "CFE_TBL_VALIDATE_CC".
    1. There are two rows, "ActiveTblFlag" and "TableName". Fill it out accordingly.
    
        Example:
        
        `CFE_TBL_INACTIVE_BUFFER` for ActiveTblFlag
        `TO_LAB_APP.MyTblDefault` for TableName 
    
        Note - TableName is the actual table name, not the table file name. 
    1. Select "Send". If successful, you should see an event:
    
        `"<Your_App_Name> validation successful for Inactive '<Your_App_Name>.<Your_Table_Name>'"`

    1. Last step is to activate it. Go back to "Table Services" menu.
    1. Select "Send" next to "CFE_TBL_ACTIVATE_CC". 
    1. Enter the table name you want to activate.
    
        Example: `TO_LAB_APP.MyTblDefault`

        Note - This is the full table name, not your table file name. 
    
        If successful, you should see an event:
        
        `"<Your_App_Name> Successfully updated '<Your_App_Name>.<Your_Table_Name>'"`

## Note(s)

1. If you have an event that says the message is invalid when you send "validate" or "activate" command, check your ground station packet definitions vs. your cFS definitions. There could be a mismatch between the lengths.

1. If you "validate" or "activate" and no events or errors occurred, your application is not passing through the "Table Manage API". "Validate" and "activate" are application level implementations. Check if you have:
    1. `CFE_TBL_Manage` implemented.
    1. `CFE_TBL_Manage` is being called.