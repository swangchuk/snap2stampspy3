# Using SNAP to generate InSAR time series data

## How run to the code?
1. Create a project folder e.g., **InSAR_Project**.
2. Inside a project folder create folders named __master__ and __slave__.
3. Put InSAR master image into __master__ folder and slaves images into __slave__ folder, respectively.
4. Open the configuration file (see **bin** folder of **snap2stampspy3**). The file ends with **.conf** extension.
5. Copy and paste the path of your project folder (step 1) into  **PROJECTFOLDER** variable.
6. Copy and paste the path of **graphs** folder into **GRAPHSFOLDER** variable.
7. Copy and paste the path of **master** folder into **MASTER** variable.
8. Assign **Swath Type** of your interestet to a **IW** variable. Supports individual swath processing (e.g, IW1) or double (e.g. IW1, IW2) or tripple (IW1, IW2, IW3).
9. Select **burst indices** (select burst that falls in your area of interest).
10. Provide coordinates of your area of interest, respectively.
11. Provide path to SNAP's **gpt**.
12. Make **bin** folder of **snap2stampspy3** your current working directory at the command prompt.
13. Execute python files as: python filename.py configuration\_filename.conf (e.g. ***python split\_multi\_swaths\_master\_sw.py  asc\_2017\_2019\_multi\_ms.conf***).
14. For processing **single swath**, execute Python files sequentially: ***1.*** split\_multi\_swaths\_master\_sw.py; ***2.*** split\_multi\_swaths\_slaves\_sw.py; ***3.*** coreg\_ifg\_topsar_multi\_swaths\_sw.py
15. For processing **multiple swaths**, execute Python files sequentially: ***1.*** split\_multi\_swaths\_master\_sw.py; ***2.*** split\_multi\_swaths\_slaves\_sw.py; ***3.*** merge\_multi\_swaths.py; ***4.*** coreg\_ifg\_topsar_multi\_swaths\_sw.py

