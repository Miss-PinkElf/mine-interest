"""本机 Provider 设置仓储。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.repositories.tables import ProviderSettingsRow


class ProviderSettingsRepository:
    """读写单例式本地 Provider 配置。"""

    # 个人本地模式固定使用的设置行主键。
    SINGLETON_ID = "local"

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self) -> ProviderSettingsRow | None:
        """读取当前 Provider 设置行。"""
        return self._session.get(ProviderSettingsRow, self.SINGLETON_ID)

    def upsert(
        self,
        *,
        base_url: str,
        model_name: str,
        api_key: str | None,
    ) -> ProviderSettingsRow:
        """创建或更新本地 Provider 设置。"""
        row = self.get()
        if row is None:
            row = ProviderSettingsRow(id=self.SINGLETON_ID)
            self._session.add(row)
        row.base_url = base_url
        row.model_name = model_name
        if api_key is not None and api_key != "":
            row.api_key = api_key
        elif row.api_key is None:
            row.api_key = ""
        self._session.flush()
        return row
