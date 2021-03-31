from dotenv import find_dotenv
from pydantic import BaseSettings


class RedisSettings(BaseSettings):
    REDIS_PORT: int
    REDIS_HOST: str
    DB: int
    REDIS_PASSWORD: str

    class Config:
        env_file = find_dotenv(filename="my_dotenv.env.dev")


redis_cfg = RedisSettings()


class SubnetVarsSettings(BaseSettings):
    SUBNET_PREFIX: int
    WAIT_UNBAN_T: int
    TRACK_IP_T: int

    class Config:
        env_file = find_dotenv(filename="my_dotenv.env.dev")


subnet_vars_cfg = SubnetVarsSettings()
