import csv

original_csv = 'csv/movies_2018_2025.csv'
manual_csv = 'csv/fixed_asian_movies.csv'
final_csv = 'csv/fixed_movies_2018_2025.csv'

with open(original_csv, 'r', encoding='gbk') as f:
    reader = csv.DictReader(f)
    original_rows = list(reader)

with open(manual_csv, 'r', encoding='gbk') as f:
    reader = csv.DictReader(f)
    manual_dict = {f"{row['movie_name']}_{row['release_year']}_{row['duration']}": row for row in reader}

for i, row in enumerate(original_rows):
    key = f"{row['movie_name']}_{row['release_year']}_{row['duration']}"
    if key in manual_dict:
        original_rows[i] = manual_dict[key]

fieldnames = original_rows[0].keys()
with open(final_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(original_rows)

print(f"Total rows: {len(original_rows)}")
