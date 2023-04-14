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
##### Create .env

```shell
cat <<EOF > ./.env
# API key of telegram
API_KEY_TELEGRAM="your token"
# Email server
EMAIL_SERVICE_HOST="mail.ru"
# Email login
EMAIL_LOGIN="123@mail.ru"
# Email password
EMAIL_PASSWORD="123456"
# Port for ssl connection to the server,
# usually 993 (not required for outlook)
EMAIL_SERVICE_SSL_PORT=XXX
# Email of the sender from whom the necessary letters come
EMAIL_SENDER="123@mail.ru"
# Time interval for checking mail, for example, check email every 10 minutes
EMAIL_CHECK_TIME_MIN=1
# Telegram user ID to whom we send received email message
ADMIN_ID_TELEGRAM=123456
EOF
```
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
