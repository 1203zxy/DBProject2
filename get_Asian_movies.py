import csv

input_csv = 'csv/movies_2018_2025.csv'
output_csv = 'csv/asian_movies.csv'

asian_countries = ['China', 'Hong Kong', 'Taiwan', 'Japan', 'Vietnam', 'North Korea', 'South Korea']

with open(input_csv, 'r', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    rows = [row for row in reader if row['country'] in asian_countries]

with open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
    if rows:
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)

print(f"Extracted {len(rows)} Asian movies to {output_csv}")