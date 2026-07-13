from pathlib import Path
import shutil
paths = [
'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2025-03-31 233419.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2026-06-19 at 7.55.53 PM.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2026-06-05 at 5.30.13 PM.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2024-12-23 230611.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot (4).png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot (101).png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2026-06-16 at 11.29.09 PM.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2026-06-04 at 4.15.16 PM.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot (97).png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot (18).png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2026-06-06 at 8.01.07 PM.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2026-06-20 at 8.24.50 PM.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2026-06-14 at 4.34.09 PM.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot_20250722-014243.Instagram.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2026-06-07 at 1.04.48 AM.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot_20250718-164805.LinkedIn.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2026-06-06 at 11.58.37 PM.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot (34).png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2025-04-01 003528.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2025-06-30 150702.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2026-06-07 at 3.53.26 PM.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot (66).png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2026-04-10 at 3.26.11 PM.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2026-06-01 at 7.58.29 PM.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot (256).png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot_20250223-183957.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2024-12-18 233740.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2026-05-28 at 11.09.06 PM.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2026-05-22 at 7.24.50 PM.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot (112).png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot (5).png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2026-05-22 at 7.24.41 PM.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2026-05-28 at 10.42.36 PM.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot_20250324-092756.Instagram.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot_20250317-141521.YouTube.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2026-05-28 at 11.08.46 PM.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2026-05-28 at 11.09.14 PM.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot 2026-06-18 at 8.06.49 PM.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot_20250719-015915.Instagram.png'
,'/Users/sankalpomar/Pictures/Screenshots/Screenshot (26).png'

]

dest = Path("/Users/sankalpomar/Pictures/cluster_review").expanduser()
dest.mkdir(exist_ok=True)

for p in paths:
    shutil.copy2(p, dest)

print(dest)