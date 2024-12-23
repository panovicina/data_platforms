# GreenPlum

## 1. Подключение к машине, где развернут GreenPlum

```
ssh user@<IP-address>
```

## 2. Работа с утилитой

Проверьте, видит ли bash утилиту psql. Если нет, то выполните следующую команду:

```
source /usr/local/greenplum-db/greenplum_path.sh
```

Теперь подключитесь к базе данных:

```
psql -d idp
```

## 3. Чтение файлов с помощью psql:

Теперь откройте второе окно терминала.
Сначала необходимо выбранный файл загрузить на машину.
Сделаем это с помощью команды для безопасной передачи файлов через ssh:

```
scp apple.csv user@<IP-address>:~
```

Убедимся, что файл скопирован. 

Подключитесь к удаленной машине:

```
ssh user@<IP-address>
```
```
ls -l apple.csv

-rw-r--r-- 1 user user 1990 Dec 23 16:44 apple.csv
```

Запускаем gpfdist:

```
gpfdist
```

### Создаем External table:

Вернемся в первое окно терминала, где подключались к базе данных.

Создаем External table:

```sql
CREATE EXTERNAL TABLE financial_data_apple (
    year INTEGER,
    ebitda_millions NUMERIC(10, 2),
    revenue_millions NUMERIC(10, 2),
    gross_profit_millions NUMERIC(10, 2),
    op_income_millions NUMERIC(10, 2),
    net_income_millions NUMERIC(10, 2),
    eps NUMERIC(10, 2),
    shares_outstanding NUMERIC(10, 3),
    year_close_price NUMERIC(10, 2),
    total_assets_millions NUMERIC(10, 2),
    cash_on_hand_millions NUMERIC(10, 2),
    long_term_debt_millions NUMERIC(10, 2),
    total_liabilities_millions NUMERIC(10, 2),
    gross_margin NUMERIC(5, 2),
    pe_ratio NUMERIC(10, 2),
    employees INTEGER
)
LOCATION ('gpfdist://localhost:8080/apple.csv')
FORMAT 'CSV' (DELIMITER ',' HEADER);
```

Проверим, что данные корректно загружаются из внешней таблицы:

```sql
SELECT * FROM financial_data_apple LIMIT 5;

   year | ebitda_millions  | revenue_millions | gross_profit_millions | op_income_millions | net_income_millions  |  eps  | shares_outstanding  | year_close_price | total_assets_millions  | cash_on_hand_millions  | long_term_debt_millions | total_liabilities_millions| gross_margin | pe_ratio | employees
--------+------------------+------------------+-----------------------+--------------------+----------------------+-------+---------------------+------------------+------------------------+------------------------+-------------------------+---------------------------+--------------+----------+-----------
   2024 |         134661.0 |         391035.0 |              180683.0 |           123216.0 |              93736.0 |  6.08 |           15408.000 |          243.040 |             364980.000 |              65171.000 |               85750.000 |              308030.000   |        46.21 |    39.97 |    164000
   2023 |         125820.0 |         383285.0 |              169148.0 |           114301.0 |              96995.0 |  6.13 |           15813.000 |          191.592 |             352583.000 |              61555.000 |               95281.000 |              290437.000   |        45.03 |    29.84 |    161000
   2022 |         130541.0 |         394328.0 |              170782.0 |           119437.0 |              99803.0 |  6.11 |           16326.000 |          128.582 |             352755.000 |              48304.000 |               98959.000 |              302083.000   |        43.06 |    21.83 |    164000
   2021 |         120233.0 |         365817.0 |              152836.0 |           108949.0 |              94680.0 |  5.61 |           16865.000 |          174.713 |             351002.000 |              62639.000 |              109106.000 |              287912.000   |        43.02 |    28.93 |    154000
   2020 |          77344.0 |         274515.0 |              104956.0 |            66288.0 |              57411.0 |  3.28 |           17528.000 |          129.756 |             323888.000 |              90943.000 |               98667.000 |              258549.000   |        38.78 |    35.14 |    147000
```

Создадим внутреннюю таблицу:

```sql
CREATE TABLE financial_data_apple_internal AS SELECT * FROM financial_data_apple;

NOTICE:  Table doesn't have 'DISTRIBUTED BY' clause. Creating a NULL policy entry.
NOTICE:  HEADER means that each one of the data files has a header row
SELECT 16
```

Проверим данные во внутренней таблице:

```sql
SELECT * FROM financial_data_apple_internal LIMIT 5;

   year | ebitda_millions  | revenue_millions | gross_profit_millions | op_income_millions | net_income_millions  |  eps  | shares_outstanding  | year_close_price | total_assets_millions  | cash_on_hand_millions  | long_term_debt_millions | total_liabilities_millions| gross_margin | pe_ratio | employees
--------+------------------+------------------+-----------------------+--------------------+----------------------+-------+---------------------+------------------+------------------------+------------------------+-------------------------+---------------------------+--------------+----------+-----------
   2024 |         134661.0 |         391035.0 |              180683.0 |           123216.0 |              93736.0 |  6.08 |           15408.000 |          243.040 |             364980.000 |              65171.000 |               85750.000 |              308030.000   |        46.21 |    39.97 |    164000
   2023 |         125820.0 |         383285.0 |              169148.0 |           114301.0 |              96995.0 |  6.13 |           15813.000 |          191.592 |             352583.000 |              61555.000 |               95281.000 |              290437.000   |        45.03 |    29.84 |    161000
   2022 |         130541.0 |         394328.0 |              170782.0 |           119437.0 |              99803.0 |  6.11 |           16326.000 |          128.582 |             352755.000 |              48304.000 |               98959.000 |              302083.000   |        43.06 |    21.83 |    164000
   2021 |         120233.0 |         365817.0 |              152836.0 |           108949.0 |              94680.0 |  5.61 |           16865.000 |          174.713 |             351002.000 |              62639.000 |              109106.000 |              287912.000   |        43.02 |    28.93 |    154000
   2020 |          77344.0 |         274515.0 |              104956.0 |            66288.0 |              57411.0 |  3.28 |           17528.000 |          129.756 |             323888.000 |              90943.000 |               98667.000 |              258549.000   |        38.78 |    35.14 |    147000
```
