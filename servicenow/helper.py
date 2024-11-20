import pandas as pd
from pandas import json_normalize


def convertJsonToExcel(json_data):
    df = json_normalize(json_data, sep='_')  # Flatten nested JSON with separator `_`

    # Save to Excel
    output_file = "nested_output.xlsx"
    df.to_excel(output_file, index=False)
    return
