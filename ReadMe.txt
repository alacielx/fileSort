# fileSort v1.86

## RULES:
- "Project Code" on CRL must have NO spaces***
- Hybrid showers must include the word "HYBRID" in "Project Name" - ie. Different glass thicknesses or glass types
- The first letter in "Project Name" will dictate glass thickness needed in shower - ie. "V", "S", "M" needs 1/4" glass, "R" needs 3/8" glass. If using different thickness add "HYBRID" to "Project Name"
- "Project Name" must include glass type as a separate keyword - ie. "CLR", "AGICLR", "STN", "RN", "OBS". If using different glass types add "HYBRID" to "Project Name"
- Shower glass type must match glass type in "Project Name"

* Remember to letter doors and add any production notes to pdf
* Pages with the words "Glass Order" and "Templates" will be removed

------------------------------------------------------------------

## Settings to change in fileSort.ini
- bates_letter - Letter from bates number ie. "G"123
- bates_number - Last number used from bates number ie. G"123"
- pdf_folder - Folder with Glass Orders and Installation Sheets, Glass Orders and Installation Sheets must be in the same folder
- dxf_folder - Folder with DXF files, can be the same as pdf_folder
- min_bates_number - Bates number will reset to this number after reaching max_bates_number
- max_bates_number - When bates number reaches this number it will reset to min_bates_number
- check_for_installs - Set to "True" to ignore checking for Installation Sheets
- add_folder_time = Set to "True" to name folder with intials and current time ie. "ADG 12.57 - 1.4 CLEAR", will use last batch time if within 5mins
- last_batch_time = Last time a batch was sorted
- initials = Initials for naming the folder ie. "ADG" 12.57 - 1.4 CLEAR
- separate_fsc = Place FSC DXF files in a subfolder
- time_threshold = Minutes before creating a new folder with new time