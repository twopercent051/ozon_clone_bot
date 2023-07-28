from dataclasses import dataclass

from environs import Env


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str


@dataclass
class RedisConfig:
    host: str
    port: str
    db: str


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    use_redis: bool


@dataclass
class Miscellaneous:
    ozon_token: str
    ozon_client_id: str
    orecht_login: str
    orecht_pass: str


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    rds: RedisConfig
    misc: Miscellaneous


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS"),
        ),
        db=DbConfig(
            host=env.str('DB_HOST'),
            password=env.str('DB_PASS'),
            user=env.str('DB_USER'),
            database=env.str('DB_NAME')
        ),
        rds=RedisConfig(
            host=env.str('REDIS_HOST'),
            port=env.str('REDIS_PORT'),
            db=env.str('REDIS_DB')
        ),
        misc=Miscellaneous(
            ozon_token=env.str("OZON_TOKEN"),
            ozon_client_id=env.str("OZON_CLIENT_ID"),
            orecht_login=env.str("ORECHT_LOGIN"),
            orecht_pass=env.str("ORECHT_PASS"),
        )
    )
