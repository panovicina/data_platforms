# Инструкция по развертыванию hadoop
### На всех хостах
#### Создаем нового пользователя
```bash
sudo adduser hadoop
```
и устанавливаем очень надежный пароль

#### Переходим на нового пользователя
```bash
sudo -i -u hadoop
```

#### Генерируем и копируем ключ для дальнейшего доступа
```bash
ssh-keygen 
cat # файл в котором вы записали публичный ssh ключ
```
пример публичного ключа - файл вида ```.ssh/id_ed25519.pub```

#### Сделать локальную адресацию
С помощью команды ```exit``` выйти из нового пользователя и отредактировать файл hosts
```bash 
sudo nano /etc/hosts
```
Закомментировать/удалить содержимое файла и вставить на примере следующего адрес и локальное название хоста
```
192.168.1.158 team-39-jn
192.168.1.159 team-39-nn
192.168.1.160 team-39-dn-0
192.168.1.161 team-39-dn-1
```
для проверки подключения использовать команду
```bash 
ping # локальное название хостов
```
к примеру
```bash 
ping team-39-nn
```
Теперь можно переключаться между хостами через локальное название, к примеру
```bash
ssh team-39-nn
```

### После выполнения пункта выше на всех хостах переходим на jump node на юзере hadoop
#### Соединение без паролей по ssh ключу

Записать в следущий файл все ssh хостов которые скопировали
```bash 
nano .ssh/authorized_keys
```
и скопировать на все хосты
```bash
scp .ssh/authorized_keys team-39-nn:/home/hadoop/.ssh/
scp .ssh/authorized_keys team-39-dn-0:/home/hadoop/.ssh/
scp .ssh/authorized_keys team-39-dn-1:/home/hadoop/.ssh/
```
В дальнейшем внутри юзера hadoop можно переключаться между хостами без пароля через локальные названия хостов, к примеру
```bash
ssh team-39-nn
```
#### Запустить установление hadoop
Выполнить следующую команду
```bash
wget https://downloads.apache.org/hadoop/common/hadoop-3.4.0/hadoop-3.4.0.tar.gz
```
После завершения скачивания скопировать архив на все остальные хосты
```bash 
scp hadoop-3.4.0.tar.gz  team-39-nn:/home/hadoop/
scp hadoop-3.4.0.tar.gz  team-39-dn-0:/home/hadoop/
scp hadoop-3.4.0.tar.gz  team-39-dn-1:/home/hadoop/
```
### На name node и data node-ах через пользователя hadoop
Разархивировать скопированный файл
```bash 
tar -xvzf hadoop-3.4.0.tar.gz
```
### На name node через пользователя hadoop
Узнаем где лежит java
```bash
readlink -f /usr/bin/java
```
Добавить следущие переменные в файл ```~/.profile```
```
export HADOOP_HOME=/home/hadoop/hadoop-3.4.0
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
```
Далее активировать переменные через
```bash
source ~/.profile
```
Скопировать данный файл на дата ноды
```bash
scp ~/.profile team-39-dn-0:/home/hadoop
scp ~/.profile team-39-dn-1:/home/hadoop
```
Далее в папке дистрибутива начать настраивать кластер
```bash
cd /hadoop-3.4.0/etc/hadoop
```
Добавить переменную ```JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64``` в файл с настройкой окружения ```hadoop-env.sh```
и скопировать этот файл на все ноды
```bash
scp hadoop-env.sh team-39-dn-0:/home/hadoop/hadoop-3.4.0/etc/hadoop
scp hadoop-env.sh team-39-dn-1:/home/hadoop/hadoop-3.4.0/etc/hadoop
```
Далее настроить файловую систему, сначала в файл ```core-site.xml``` добавить конфиг
```xml
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://team-39-nn:9000:9000</value>
    </property>
</configuration>

```
Потом в файл ```hdfs-site.xml``` добавить свойство репликации
```xml
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>3</value>
    </property>
</configuration>

```
В файл ```workers``` записать следующее
```
team-39-nn
team-39-dn-0
team-39-dn-1
```

И эти три файла скопировать на остальные ноды
```bash
scp core-site.xml team-39-dn-0:/home/hadoop/hadoop-3.4.0/etc/hadoop
scp core-site.xml team-39-dn-1:/home/hadoop/hadoop-3.4.0/etc/hadoop

scp hdfs-site.xml team-39-dn-0:/home/hadoop/hadoop-3.4.0/etc/hadoop
scp hdfs-site.xml team-39-dn-1:/home/hadoop/hadoop-3.4.0/etc/hadoop

scp workers team-39-dn-0:/home/hadoop/hadoop-3.4.0/etc/hadoop
scp workers team-39-dn-1:/home/hadoop/hadoop-3.4.0/etc/hadoop
```
## Запуск кластера
Форматируем name node
```bash
/home/hadoop/hadoop-3.4.0/bin/hdfs namenode -format
```

```bash
/home/hadoop/hadoop-3.4.0/sbin/start-dfs.sh
```
При запуске команды jps 
* на хосте name node должны отображаться: SecondaryNameNode, NameNode, DataNode
* на хостах data node должны отображаться: DataNode
### Остановить работу кластера
```bash
/home/hadoop/hadoop-3.4.0/sbin/stop-dfs.sh
```

## Веб интерфейс
На хосте jump node настроить конфиг для nginx, сначала скопировать дефолтный конфиг в другое место и изменить его
```bash
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/nn
```
В файле конфига ```/etc/nginx/sites-available/nn```должно содержаться следующее
```
server {
       listen 9870;

        root /var/www/html;

        # Add index.php to the list if you are using PHP
        index index.html index.htm index.nginx-debian.html;

        server_name _;

       location / {
               proxy_pass http://team-39-nn:9870;
       }
}
```
### Авторизация
Для начала установить apache2-utils и задать пароль для юзера
```bash
sudo apt-get install apache2-utils
sudo mkdir -p /etc/apache2
sudo htpasswd -c /etc/apache2/.htpasswd hadoop
```

В файле конфига ```/etc/nginx/sites-available/nn``` в ```location {}``` добавить 
```
auth_basic "NN interface";
auth_basic_user_file /etc/apache2/.htpasswd;
```
и перезагрузить nginx
```bash
sudo systemctl status nginx
```

По адресу ```http://team-39-nn:9870``` будет находиться веб интерфейс NameNode и зайти туда можно по логину hadoop и по заданному вами паролю.
