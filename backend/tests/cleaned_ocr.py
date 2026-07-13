import pandas as pd
import preprocessing_pipeline


data = pd.read_csv("ocr_result.csv")
# print(data.head())

sentences = data["text"]

with open("cleaned_ocr.txt","w") as file:
    for sentence in sentences[:10]:
        print(sentence)
        file.write(preprocessing_pipeline.cleaning_pipeline(sentence) + "\n")