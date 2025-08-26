#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Deploy Microsoft Fabric items from a Git repo to a specified Fabric workspace.
- No parameter.yml is required
- Supports only DEV and PROD environments
"""

import argparse
import logging
import sys
from pathlib import Path
from fabric_cicd import (
    FabricWorkspace,
    publish_all_items,
    unpublish_all_orphan_items,
    change_log_level,
)

DEFAULT_ITEMS = [
    "Notebook",
    "DataPipeline",
    "Lakehouse",
    "SemanticModel",
    "Report",
]

def parse_args():
    p = argparse.ArgumentParser(description="Deploy Microsoft Fabric artifacts")
    p.add_argument("--WorkspaceId", required=True, help="Target Fabric Workspace ID")
    p.add_argument("--Environment", required=True, choices=["DEV", "PROD"])
    p.add_argument("--RepositoryDirectory", required=True)
    p.add_argument("--ItemsInScope", default="all", help="Comma-list of items or 'all'")
    p.add_argument("--UnpublishOrphans", default="false")
    p.add_argument("--Debug", action="store_true")
    return p.parse_args()

def normalize_bool(val: str) -> bool:
    return str(val).strip().lower() in {"1", "true", "yes", "y", "on"}

def compute_items(scope: str):
    if scope.strip().lower() == "all":
        return DEFAULT_ITEMS
    return [t.strip() for t in scope.split(",") if t.strip()]

def main():
    args = parse_args()
    log_level = logging.DEBUG if args.Debug else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s %(levelname)s %(message)s")
    if args.Debug:
        change_log_level("DEBUG")

    repo_dir = Path(args.RepositoryDirectory).resolve()
    items = compute_items(args.ItemsInScope)
    unpublish = normalize_bool(args.UnpublishOrphans)

    logging.info("Deploying to %s workspace %s", args.Environment, args.WorkspaceId)

    try:
        ws = FabricWorkspace(
            workspace_id=args.WorkspaceId,
            environment=args.Environment,
            repository_directory=str(repo_dir),
            item_type_in_scope=items,
        )
        publish_all_items(ws)
        if unpublish:
            unpublish_all_orphan_items(ws)
        logging.info("Deployment successful ✅")
        return 0
    except Exception as e:
        logging.exception("Deployment failed ❌: %s", e)
        return 1

if __name__ == "__main__":
    sys.exit(main())
