"""Artifact Store（产物存储）：为每个 Job 维护独立本地目录。"""

from pathlib import Path

from app.core import constants


class ArtifactPathError(ValueError):
    """当相对路径试图逃逸任务产物根目录时抛出。"""


class ArtifactStore:
    """按 job_id 隔离读写本地产物，失败时也不主动删除上游文件。"""

    def __init__(self, root_dir: Path | str) -> None:
        self.root_dir = Path(root_dir).expanduser().resolve()
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def job_dir(self, job_id: str) -> Path:
        """返回任务专属产物目录，必要时自动创建。"""
        path = self.root_dir / constants.JOB_ARTIFACT_DIR_PREFIX / job_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def resolve_path(self, job_id: str, relative_path: str) -> Path:
        """将相对路径解析到任务目录内，阻止路径穿越。"""
        job_root = self.job_dir(job_id).resolve()
        target = (job_root / relative_path).resolve()
        if target != job_root and job_root not in target.parents:
            raise ArtifactPathError(
                f"产物路径越界：{relative_path!r} 不在任务目录内"
            )
        return target

    def write_text(self, job_id: str, relative_path: str, content: str) -> Path:
        """写入文本产物，自动创建中间目录。"""
        target = self.resolve_path(job_id, relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def read_text(self, job_id: str, relative_path: str) -> str:
        """读取任务内的文本产物。"""
        target = self.resolve_path(job_id, relative_path)
        return target.read_text(encoding="utf-8")

    def exists(self, job_id: str, relative_path: str) -> bool:
        """判断任务内指定产物是否存在。"""
        return self.resolve_path(job_id, relative_path).exists()
