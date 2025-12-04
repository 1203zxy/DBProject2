# pip install pandas
import pandas as pd

input_file = 'csv/fixed_movies_2018_2025.csv'
output_file = 'csv/clean_movies_2018_2025.csv'

df = pd.read_csv(input_file, encoding='gbk')

original_rows = len(df)
print(f"原始数据行数: {original_rows}")

df_cleaned = df.drop_duplicates(subset=['movie_name', 'country', 'release_year'], keep='first')

cleaned_rows = len(df_cleaned)
removed_rows = original_rows - cleaned_rows

print(f"去重后行数: {cleaned_rows}")
print(f"删除的重复行数: {removed_rows}")

df_cleaned.to_csv(output_file, index=False)
