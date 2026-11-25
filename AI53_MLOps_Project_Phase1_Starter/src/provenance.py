from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import subprocess
from pathlib import Path

import torch


def training_data_identity(
    train_manifest: Path = Path("data/processed/manifests/train.csv"),
    validation_manifest: Path = Path("data/processed/manifests/validation.csv"),
) -> str:
    """Return a deterministic identity for the training + validation manifests.

    This helper is provided because the final evaluator uses the same identity
    to verify that the selected MLflow Run matches the current prepared data.
    Do not hard-code the value.
    """
    paths = (train_manifest, validation_manifest)
    if any(not path.exists() for path in paths):
        return "unavailable"

    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _git_output(*args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            check=False,
            text=True,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


def build_run_manifest(params: dict, device: str, mlflow_run_id: str) -> dict:
    """Build deterministic experiment provenance metadata."""
    commit = _git_output("rev-parse", "HEAD")
    git_status = _git_output("status", "--porcelain")

    return {
        "git": {
            "commit": commit,
            "dirty": None if git_status is None else bool(git_status),
        },
        "data": {
            "training_data_identity": training_data_identity(),
        },
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "torchvision": _package_version("torchvision"),
            "dvc": _package_version("dvc"),
            "mlflow": _package_version("mlflow"),
            "platform": platform.platform(),
            "cuda_runtime": torch.version.cuda,
        },
        "execution": {
            "device": device,
            "random_state": int(params["train"]["random_state"]),
            "mlflow_run_id": mlflow_run_id,
        },
        "configuration": {
            "image_size": int(params["data"]["image_size"]),
            "train": dict(params["train"]),
            "augmentation": dict(params["augmentation"]),
        },
    }


def write_run_manifest(params: dict, device: str, mlflow_run_id: str, path: Path) -> dict:
    manifest = build_run_manifest(params, device, mlflow_run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest
