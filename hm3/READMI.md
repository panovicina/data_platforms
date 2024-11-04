# Инструкция по развертыванию Apache Hive с PostgreSQL

Данная инструкция пошагово описывает установку и настройку Apache Hive с использованием PostgreSQL для хранения метаданных.

### Шаг 1: Установка и настройка Hive

1. Находясь на JumpNode под пользователем team переключаемся на пользователя `hadoop`:
    ```bash
    sudo -i -u hadoop
    ```

2. Скачиваем архив с Apache Hive:
    ```bash
    wget https://archive.apache.org/dist/hive/hive-4.0.1/apache-hive-4.0.1-bin.tar.gz
    ```

3. Далее необходимо распаковать архив:
    ```bash
    tar -xvzf apache-hive-4.0.1-bin.tar.gz
    ```

4. Переходим в директорию с установленным Hive:
    ```bash
    cd apache-hive-4.0.1-bin/
    ```

5. Проверяем текущий путь:
    ```bash
    pwd
    ```

6. Устанавливаем переменные окружения. Путь, полученный в шаге 5 используем для HIVE_HOME:
    ```bash
    export HIVE_HOME=/home/hadoop/apache-hive-4.0.1-bin
    export PATH=$HIVE_HOME/bin:$PATH
    ```

### Шаг 2: Подготовка HDFS

1. Теперь необходимо подключиться к NameNode:
    ```bash
    ssh team-39-nn
    ```

2. Создаем директорию для хранения данных Hive в HDFS:
    ```bash
    hdfs dfs -mkdir -p /user/hive/warehouse
    ```

3. Устанавливаем права на запись для нужных нам директорий:
    ```bash
    hdfs dfs -chmod g+w /tmp
    hdfs dfs -chmod g+w /user/hive/warehouse
    ```

4. Проверяем директории HDFS:
    ```bash
    hdfs dfs -ls /
    ```
    Мы должны увидеть две директории: `/tmp` и `/user`.

5. Дальнейшие шаги нужно выполнять на JumpNode, поэтому выходим из NameNode:
    ```bash
    exit
    ```

### Шаг 3: Настройка конфигурации Hive

1. Мы находимся на JumpNode. Теперь переходим в директорию с конфигурационными файлами Hive:
    ```bash
    cd /apache-hive-4.0.1-bin/conf/
    ```

2. Копируем шаблон файла конфигурации:
    ```bash
    cp hive-default.xml.template hive-site.xml
    ```

3. Откроем файл `hive-site.xml`:
    ```bash
    vim hive-site.xml
    ```

4. Добавляем следующие настройки в файл `hive-site.xml`:
    ```xml
    <property>
        <name>hive.server2.authentication</name>
        <value>NONE</value>
    </property>
    <property>
        <name>hive.metastore.warehouse.dir</name>
        <value>/user/hive/warehouse</value>
    </property>
    <property>
        <name>hive.server2.thrift.port</name>
        <value>5433</value>
    </property>
    ```

### Шаг 4: Настройка переменных окружения

1. Открываем файл `hive-env.sh` для редактирования:
    ```bash
    vim hive-env.sh
    ```

2. Вставляем следующие строки:
    ```bash
    export HIVE_HOME=/home/hadoop/apache-hive-4.0.1-bin
    export HIVE_CONF_DIR=$HIVE_HOME/conf
    export HIVE_AUX_JARS_PATH=$HIVE_HOME/lib/*
    ```

### Шаг 5: Установка PostgreSQL

Перед выполнением следующих шагов необходимо переключиться на NameNode. Как это сделать было описано ранее.

1. Находясь на NameNode, выполняем следующую команду для установки PostgreSQL:
    ```bash
    sudo apt install postgresql postgresql-contrib
    ```

2. Проверяем статус PostgreSQL:
    ```bash
    sudo systemctl status postgresql
    ```
   При успешной установке мы увидим такой вывод:

   ```bash
   postgresql.service - PostgreSQL RDBMS
     Loaded: loaded (/usr/lib/systemd/system/postgresql.service; enabled; prese>
     Active: active (exited) since Mon 2024-11-04 16:08:58 UTC; 2h 12min ago
    Process: 38454 ExecStart=/bin/true (code=exited, status=0/SUCCESS)
   Main PID: 38454 (code=exited, status=0/SUCCESS)
        CPU: 886us

   Nov 04 16:08:58 team-39-nn systemd[1]: Starting postgresql.service - PostgreSQL>
   Nov 04 16:08:58 team-39-nn systemd[1]: Finished postgresql.service - PostgreSQL>
   ```

3. Подключаемся к PostgreSQL для создания базы данных:
    ```bash
    sudo -i -u postgres
    psql
    ```

4. Создаем базу данных `metastore`:
    ```sql
    create database metastore;
    ```

5. Создаем пользователя `hive` с паролем 'hive' для подключения к базе данных:
    ```sql
    create user hive with password 'hive';
    ```

6. Даем пользователю `hive` все права на базу данных `metastore`.
    ```sql
    grant all privileges on database "metastore" to hive;
    ```

7. Выходим из PostgreSQL.
    ```bash
    exit
    ```

### Шаг 6: Настройка доступа PostgreSQL для внешних хостов

В следующих шагах все еще находимся на NameNode.

1. Открываем файл конфигурации PostgreSQL для редактирования:
    ```bash
    sudo vim /etc/postgresql/16/main/pg_hba.conf
    ```

2. Добавляем следующую строку в разделе `# IPv4 local connections`:
    ```plaintext
    host    metastore       hive            <jumpnode-ip>/32         password
    ```
   И тут же удаляем данную строку:
    ```plaintext
    host    all             all             127.0.0.1/32            scram-sha-256
    ```
3. В конфиге в секции "CONNECTIONS AND AUTHENTICATION" нужно добавить следующее:
   
   ```bash
    listen_addresses = '<namenode-ip>'
    ```

4. Перезапускаем PostgreSQL для применения изменений.
    ```bash
    sudo systemctl restart postgresql
    ```
   И так же проверяем статус, как делали ранее:

    ```bash
    sudo systemctl status postgresql
    ```
   

### Шаг 7: Загрузка JDBC-драйвера PostgreSQL

Следующие шаги выполняем на JumpNode. Для этого необходимо выйти с NameNode, сделаем это:
```bash
exit
```

1. Переходим в директорию библиотеки Hive:
    ```bash
    cd /home/hadoop/apache-hive-4.0.1-bin/lib/
    ```
   
2. Скачиваем драйвер JDBC для PostgreSQL:
    ```bash
    wget https://jdbc.postgresql.org/download/postgresql-42.7.4.jar
    ```

### Шаг 8: Конфигурация подключения к базе данных в Hive

1. Переходим в директорию с конфигурациями Hive.
    ```bash
    cd ../conf/
    ```

2. Открываем файл `hive-site.xml` для редактирования:
    ```bash
    vim hive-site.xml
    ```

3. Добавляем следующие настройки в файл `hive-site.xml`:
    ```xml
    <property>
        <name>javax.jdo.option.ConnectionURL</name>
        <value>jdbc:postgresql://${NAMENODE_HOST}:5432/metastore</value>
    </property>
    <property>
        <name>javax.jdo.option.ConnectionDriverName</name>
        <value>org.postgresql.Driver</value>
    </property>
    <property>
        <name>javax.jdo.option.ConnectionUserName</name>
        <value>hive</value>
    </property>
    <property>
        <name>javax.jdo.option.ConnectionPassword</name>
        <value>${HIVE_POSTGRES_PASSWORD}</value>
    </property>
    ```
   
   В нашем случае NAMENODE_HOST = 192.168.1.159, HIVE_POSTGRES_PASSWORD = 'hive'.
   

### Шаг 9: Инициализация схемы базы данных

1. Переходим в директорию apache-hive-4.0.1-bin:
    ```bash
    cd ../
    ```

2. Инициализируем схему базы данных.
    ```bash
    bin/schematool -dbType postgresql -initSchema
    ```

3. Теперь можем запустить Hive:
   ```bash
   hive \
    --hiveconf hive.server2.enable.doAs=false \
    --hiveconf hive.security.authorization.enabled=false \
    --service hiveserver2 \
    1>> /tmp/hs2.log 2>> /tmp/hs2.log
   ```

На этом установка и настройка завершены, Hive готов к использованию.
