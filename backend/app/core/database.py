"""SQLite 引擎、会话与表结构初始化。"""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core import constants


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类，供仓储表模型继承。"""


def build_sqlite_url(database_path: Path) -> str:
    """将本地文件路径转换为 SQLAlchemy SQLite URL。"""
    resolved = database_path.expanduser().resolve()
    return f"{constants.SQLITE_URL_PREFIX}{resolved}"


def create_db_engine(database_path: Path):
    """创建指向本地 SQLite 文件的引擎，并确保父目录存在。"""
    database_path = database_path.expanduser().resolve()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    # check_same_thread=False 允许 FastAPI 与测试在不同线程复用连接。
    return create_engine(
        build_sqlite_url(database_path),
        connect_args={"check_same_thread": False},
    )


def create_session_factory(database_path: Path) -> sessionmaker[Session]:
    """创建绑定到本地 SQLite 的会话工厂，并初始化表结构。"""
    engine = create_db_engine(database_path)
    # 延迟导入，避免核心模块与仓储表模型循环依赖。
    from app.repositories import tables  # noqa: F401

    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


@contextmanager
def session_scope(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    """提供提交/回滚边界清晰的会话作用域。"""
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
