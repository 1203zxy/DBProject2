# Database Enhancement

该项目从 The Movie Database 上获取了自2018年至2025年热度最高的八千部电影，并对这些电影进行处理，最终将新的七千部电影纳入数据库，同时确保数据的一致性和完整性，确保更新后的数据库保持所有必要的关系和约束，确保更新后的SQL文件能够同时被PostgreSQL和openGauss支持

## 项目结构
-  **csv文件夹**：储存了所有csv类型的文件
-  **db文件夹**：储存了db类型的文件
-  **sql文件夹**：储存了sql类型的文件
-  **/.py文件**：处理数据的脚本
-  **/.tst文件**：修改的原来sql文件中的约束，使其能适配新插入的数据集以及 openGauss

## 操作方法

- ### 从 The Movie Database 上获取了自2018年至2025年热度最高的八千部电影
  利用 spider_tmdb.py 文件从 The Movie Database 上获取数据并且写入 movies_2018_2025.csv 文件中
- ### 处理亚洲国家的人名 fistname 与 surname 颠倒的情况
  **1.** 利用 get_Asian_movies.py 文件从 movies_2018_2025.csv 文件中提取出亚洲国家的数据并写入 asian_movies.csv   
  **2.** 人工找出 asian_movies.csv 文件中 fistname 与 surname 颠倒的数据，并对其矫正，将文件另存为 fixed_asian_movies.csv   
  **3.** 利用 merge.py 文件将处理完的 fixed_asian_movies.csv 替换掉原始文件 movies_2018_2025.csv 中相同的数据，并将结果写入 fixed_movies_2018_2025.csv   
- ### 处理重复数据
  利用 clean.py 文件清除重复的数据，将最终结果写入 clean_movies_2018_2025.csv
- ### 生成 sql 文件
  利用 generate_sql.py 文件，先读取 create_db.py 生成的 filmdb.db ，记录其中已经出现过的演员和导演，再结合 clean_movies_2018_2025.csv 中的数据按照原数据库的表构建插入语句，生成 import_movies.sql
- ### 获取最终的sql文件
  人工将 import_movies.sql 文件中的语句复制到 filmdb.sql 中，形成最终的 new_filmdb.sql 文件

## 运行结果
  - 项目均在 Python==3.9 pandas==1.2.4 环境下运行
  - new_filmdb.sql 文件能够同时被PostgreSQL和openGauss支持，且均运行无误
 
