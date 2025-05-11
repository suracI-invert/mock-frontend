from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
    YamlConfigSettingsSource,
)

from .connect import ConnectionSettings


class Settings(BaseSettings):
    connection: ConnectionSettings

    model_config = SettingsConfigDict(
        env_nested_delimiter="__", yaml_file="config/config.yaml"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            YamlConfigSettingsSource(
                settings_cls,
            ),
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
