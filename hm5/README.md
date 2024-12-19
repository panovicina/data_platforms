# Запуск ETL процесса. Prefect

## 1. Проверка данных Hadoop

В предыдущих домашних заданиях мы записали данные на Hadoop, поэтому в первую очередь стоит убедиться в наличии данных:

```
sudo -i -u hadoop
hdfs dfs -ls /input
```

Если данные есть, то вывод будет примерно таким:

```
-rw-r--r--   3 hadoop supergroup       564707549 2024-12-10 19:11 /input/data-20241101-structure-20180828.csv
```

## 2. Установка зависимостей

Активация виртуальной среды:

```
source venv/bin/activate
```

Установка зависимостей:

```
pip install ipython
pip install pyspark
pip install onetl
pip install prefect
```

Запуск интерактивной оболочки ipython:

```
ipython
```

## 3. Запуск скрипта с ETL процессом:

Создадим файл для записи скрипта:

```
nano data_processing.py
```

Далее скопируйте содержимое файла data_processing.py в свой файл, файл data_processing.py также находится в директории домашнего задания.

И запустите ETL процесс:

```
python data_processing.py
```
