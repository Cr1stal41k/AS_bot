import json

from pydantic import BaseModel
from typing import List

class ServerConfig(BaseModel):
    email_service_host: str
    email_login: str
    email_password: str
    email_service_ssl_port: int
    email_check_time_min: int
    email_sender: str
    admin_id_telegram: int
    api_key_telegram: str
    email_subject: str

def load_servers_config(config_path: str = "settings\env.json") -> List[ServerConfig]:
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Валидируем каждый сервер из списка SERVERS
    servers = [ServerConfig(**server) for server in data["SERVERS"]]
    return servers
# Глобальная переменная — список всех серверов


servers_config = load_servers_config()
all_email_subjects = [server.email_subject for server in servers_config]
