# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "matplotlib>=3.10.8",
#     "pandas>=2.3.3",
# ]
# ///


import matplotlib.pyplot as plt
import pandas as pd
from io import StringIO

# CSV data
csv_data = """reference,reading
0.0,0.0
1850.0,2580.0
3070.0,4311.0
4280.0,5755.0
5470.0,7183.0
6640.0,8684.0
7800.0,9787.0
8920.0,10958.0
9890.0,11947.0
10920.0,13030.0
11740.0,13734.0
12710.0,14644.0
13660.0,15481.0
15660.0,17243.0
16890.0,18236.0
18220.0,19337.0
19400.0,20170.0
19540.0,20288.0
20900.0,21385.0
22000.0,22132.0
23000.0,22836.0
"""

# Load into DataFrame
df = pd.read_csv(StringIO(csv_data))

# Create figure
# fig, ax = plt.subplots(figsize=(6, 8))
# ax.axis('off')

# Create table
plt.plot(
    df["reading"],
    df["reference"],
    # loc='center',
    # cellLoc='center'
)

# # Styling
# table.auto_set_font_size(False)
# table.set_fontsize(10)
# table.scale(1, 1.3)

plt.title("Reference vs Reading (lux)", pad=12)
plt.xlabel("VEML7700 ")
plt.ylabel("R8100SD")
# plt.tight_layout()
plt.show()

