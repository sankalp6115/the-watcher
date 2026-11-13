import time
from tqdm import tqdm

# Wrap range() or any list with tqdm()
for i in tqdm(range(100), desc="Processing"):
    time.sleep(0.05)