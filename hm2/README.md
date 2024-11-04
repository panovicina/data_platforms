# Запуск YARN и настройка веб-интерфейсов
## Настройка mapred и YARN

В NameNode, под пользователем hadoop в папке ```hadoop-3.4.0/etc``` редактируем конфиг ```mapred-site.xml```, добавляем следующие свойства
```xml
<configuration>
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
    <property>
        <name>mapreduce.application.classpath</name>
        <value>$HADOOP_HOME/share/hadoop/mapreduce/*:$HADOOP_HOME/share/hadoop/mapreduce/lib/*</value>
    </property>
</configuration>
```

Далее настраиваем ```yarn-site.xml```, запись следующего в конфигурацию

```xml
<configuration>
    <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>
    <property>
        <name>yarn.nodemanager.env-whitelist</name>
        <value>JAVA_HOME,HADOOP_COMMON_HOME,HADOOP_HDFS_HOME,HADOOP_CONF_DIR, CLASSPATH_PREPEND_DISTCACHE,HADOOP_YARN_HOME,PATH,LANG,TZ,HADOOP_MAPRED_HOME</value>
    </property>
</configuration>
```

Копирование отредактированных файлов на другие хосты
```bash 
scp mapred-site.xml team-39-dn-0:/home/hadoop/hadoop-3.4.0/etc/hadoop
scp mapred-site.xml team-39-dn-1:/home/hadoop/hadoop-3.4.0/etc/hadoop

scp yarn-site.xml team-39-dn-0:/home/hadoop/hadoop-3.4.0/etc/hadoop
scp yarn-site.xml team-39-dn-1:/home/hadoop/hadoop-3.4.0/etc/hadoop
```
### Запуск YARN и mapred
В запущенном кластере выполнить на NameNode запуск YARN и mapred
```bash 
sbin/start-yarn.sh
mapred --daemon start historyserver
```

## Веб интерфейс
Принцип подключения отличается от веб интерфейса NameNode из дз1 только портами и названиями файлов 

На хосте jump node настроить конфиг для nginx, сначала скопировать конфиг NameNode в другое место и изменить его
```bash
sudo cp /etc/nginx/sites-available/nn /etc/nginx/sites-available/ya
```
В файле конфига ```/etc/nginx/sites-available/ya```должно содержаться следующее
``` 
server {
       listen 8088;

        root /var/www/html;

        # Add index.php to the list if you are using PHP
        index index.html index.htm index.nginx-debian.html;

        server_name _;

       location / {
               proxy_pass http://team-39-nn:8088;
               auth_basic "YA interface";
               auth_basic_user_file /etc/apache2/.htpasswd;
       }
}
```
изменили порты на ```8088``` и переименовали ```auth_basic```

тоже самое с historyserver
```bash
sudo cp /etc/nginx/sites-available/nn /etc/nginx/sites-available/dh
```
В файле конфига ```/etc/nginx/sites-available/dh```должно содержаться следующее
``` 
server {
       listen 19888;

        root /var/www/html;

        # Add index.php to the list if you are using PHP
        index index.html index.htm index.nginx-debian.html;

        server_name _;

       location / {
               proxy_pass http://team-39-nn:19888;
               auth_basic "DH interface";
               auth_basic_user_file /etc/apache2/.htpasswd;
       }
}
```
изменили порты на ```19888``` и переименовали ```auth_basic```

По адресам ```http://team-39-nn:8088``` и ```http://team-39-nn:19888``` будут находиться веб интерфейсы YARN и HistoryServer соответственно и зайти туда можно по логину hadoop и по заданному вами паролю.
