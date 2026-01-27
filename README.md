# Install "Automation service chat-bot" in Linux

## Getting Started

### Preparing

#### Clone git repository

```shell
git clone https://github.com/Cr1stal41k/AS_bot.git
```
#### Move in directory AS_bot

```shell
cd AS_bot/
```
#### Create files

##### Create db.csv

```shell
cat <<EOF > ./src/db/db.csv
Telegram_ID
1234567
7654321
EOF
```
##### Create env.json

В папке settings, нужно создать файл env.json

{
    "SERVERS":
    [
        {
            "email_service_host":"email_service_host",
            "email_login":"email_login",
            "email_password":"email_password",
            "email_service_ssl_port":993,
            "email_check_time_min":1,
            "email_sender":"email_sender",
            "admin_id_telegram":11111,
            "api_key_telegram":"admin_id_telegram",
            "email_subject":"spas"

        },
       {
            "email_service_host":"email_service_host",
            "email_login":"email_login",
            "email_password":"email_password",
            "email_service_ssl_port":993,
            "email_check_time_min":1,
            "email_sender":"email_sender",
            "admin_id_telegram":3333,
            "api_key_telegram":"admin_id_telegram",
            "email_subject":"sdo"

        },

    ]
}


#### Run the script

```shell
chmod +x install.sh && ./install.sh
```
#### Define PID

```shell
ps -aux | grep 'python -m src.main'
```
#### Stop process

```shell
kill PID
```



#### Development
pip install poetry
poetry env use C:\Users\User\AppData\Local\Programs\Python\Python310\python.exe 

# Create virtualvenv .venv local
poetry config virtualenvs.in-project true
poetry install
poetry install --only main
poetry run python -m src.main