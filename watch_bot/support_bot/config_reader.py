from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    # Желательно вместо str использовать SecretStr 
    # для конфиденциальных данных, например, токена бота
    bot_token: SecretStr
    db_host:SecretStr
    db_port: SecretStr
    db_password: SecretStr
    db_name: SecretStr
    db_user: SecretStr
    chat_id: SecretStr
    ads_chat_id: SecretStr
    main_chat_id: SecretStr
    help_chat: SecretStr
    logging: SecretStr
    workers_list: SecretStr
    admin_list: SecretStr
    api_id: SecretStr
    api_hash: SecretStr
    redis_link: SecretStr
    # Начиная со второй версии pydantic, настройки класса настроек задаются
    # через model_config
    # В данном случае будет использоваться файла .env, который будет прочитан
    # с кодировкой UTF-8
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


# При импорте файла сразу создастся 
# и провалидируется объект конфига, 
# который можно далее импортировать из разных мест
config = Settings()
