import sqlite3
import csv

DB_PATH = "filmdb_real.db"
CSV_PATH = "csv/movies_with_code.csv"
OUTPUT_SQL = "sql/import_movies.sql"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 1. 获取当前最大ID
cur.execute("SELECT MAX(movieid) FROM movies")
max_movieid = cur.fetchone()[0] or 0
next_movieid = max_movieid + 1

cur.execute("SELECT MAX(peopleid) FROM people")
max_peopleid = cur.fetchone()[0] or 0
next_peopleid = max_peopleid + 1

print(f"当前最大 movieid: {max_movieid} → 新电影从 {next_movieid} 开始")
print(f"当前最大 peopleid: {max_peopleid} → 新人物从 {next_peopleid} 开始")

# 2. 加载所有已有人物用于去重
cur.execute("SELECT peopleid, first_name, surname, born FROM people")
person_cache = {}
for pid, fn, sn, born in cur.fetchall():
    fn_key = (fn or "").strip().lower().replace("'", "''")
    sn_key = (sn or "").strip().lower().replace("'", "''")
    born_key = born if born is not None else None
    key = (fn_key, sn_key, born_key)
    if key not in person_cache:
        person_cache[key] = pid

# 3. 准备输出
movies_sql = []
people_sql = []
credits_sql = []

new_person_count = 0
reuse_person_count = 0
skipped_movies_count = 0


def escape_sql_string(text):
    if not text:
        return ""
    return str(text).replace("'", "''")

def get_or_create_person(firstname, lastname, gender_str, birth_str, death_str):
    global next_peopleid, new_person_count, reuse_person_count

    fn = (firstname or "").strip()
    ln = (lastname or "").strip()
    if not ln:
        return None, False

    born = None
    if birth_str and birth_str.strip():
        try:
            born = int(birth_str.split("/")[0])
        except:
            try:
                born = int(float(birth_str))
            except:
                pass

    key = (escape_sql_string(fn).lower(),
           escape_sql_string(ln).lower(),
           born if born else None)

    if key in person_cache:
        reuse_person_count += 1
        return person_cache[key], False

    pid = next_peopleid
    person_cache[key] = pid
    next_peopleid += 1
    new_person_count += 1

    gender = "F" if gender_str and "female" in gender_str.lower() else "M" if gender_str and "male" in gender_str.lower() else None
    died = "NULL"
    if death_str and death_str.strip() and death_str.lower() != "nan":
        try:
            died = int(death_str.split("/")[0])
        except:
            died = "NULL"

    safe_fn = escape_sql_string(fn)
    safe_ln = escape_sql_string(ln)

    people_sql.append(
        f"({pid}, '{safe_fn}', '{safe_ln}', {born or 'NULL'}, {died or 'NULL'}, '{gender or ''}')"
    )
    return pid, True

with open(CSV_PATH, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        title = row["movie_name"].strip()
        if not title:
            continue

        country_code = row["country_code"].strip().lower()

        if country_code == 'xx':
            skipped_movies_count += 1
            continue

        try:
            year = int(float(row["release_year"]))
        except:
            continue

        duration = row["duration"].strip()
        duration = int(float(duration)) if duration and duration != "0" else "NULL"

        safe_title = escape_sql_string(title)

        movies_sql.append(
            f"({next_movieid}, '{safe_title}', '{country_code}', {year}, {duration if duration != 'NULL' else 'NULL'})")

        current_movieid = next_movieid

        result = get_or_create_person(
            row["director_firstname"],
            row["director_lastname"],
            row["director_gender"],
            row["director_birthyear"],
            row["director_deathyear"]
        )
        if result and result[0] is not None:
            dir_pid, _ = result
            credits_sql.append(f"({current_movieid}, {dir_pid}, 'D')")

        for i in range(1, 4):
            result = get_or_create_person(
                row[f"actor{i}_firstname"],
                row[f"actor{i}_lastname"],
                row[f"actor{i}_gender"],
                row[f"actor{i}_birthyear"],
                row[f"actor{i}_deathyear"]
            )
            if result and result[0] is not None:
                pid, _ = result
                credits_sql.append(f"({current_movieid}, {pid}, 'A')")

        next_movieid += 1

conn.close()

with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
    f.write(f"-- 新增电影 {len(movies_sql)} 部\n")
    f.write(f"-- 新增人物 {new_person_count} 人，复用旧人物 {reuse_person_count} 人\n")
    f.write(f"-- 跳过国家代码为'xx'的电影：{skipped_movies_count} 部\n\n")

    f.write("INSERT INTO movies (movieid, title, country, year_released, runtime) VALUES\n")
    f.write(',\n'.join(movies_sql) + ';\n\n')

    if people_sql:
        f.write("INSERT INTO people (peopleid, first_name, surname, born, died, gender) VALUES\n")
        f.write(',\n'.join(people_sql) + ';\n\n')

    if credits_sql:
        f.write("INSERT INTO credits (movieid, peopleid, credited_as) VALUES\n")
        f.write(',\n'.join(credits_sql) + ';\n')

print(f"共成功处理电影：{len(movies_sql)} 部")
print(f"跳过国家代码为'xx'的电影：{skipped_movies_count} 部")
print(f"新增人物：{new_person_count} 人 , 复用旧人物：{reuse_person_count} 人")