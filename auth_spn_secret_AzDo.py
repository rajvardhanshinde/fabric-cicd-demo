import argparse
import os
import yaml
from fabric_cicd import FabricWorkspace, publish_all_items, unpublish_all_orphan_items

# ---------------------------
# Parse command-line arguments
# ---------------------------
parser = argparse.ArgumentParser(description='Deploy items to Fabric')
parser.add_argument('--WorkspaceId', type=str, help='Target workspace ID')
parser.add_argument('--Environment', type=str, help='Environment (e.g., TEST, PROD)')
parser.add_argument('--RepositoryDirectory', type=str, help='Path to repo directory')
parser.add_argument('--ItemsInScope', type=str, default="all",
                    help='Comma-separated list of item types to deploy (Notebook, Report, SemanticModel)')
parser.add_argument('--ArtifactsYaml', type=str, default=None,
                    help='Optional path to artifacts YAML file for per-item deployment')

args = parser.parse_args()

# ---------------------------
# Determine items to deploy
# ---------------------------
if args.ArtifactsYaml:
    if not os.path.exists(args.ArtifactsYaml):
        raise FileNotFoundError(f"Artifacts YAML file not found: {args.ArtifactsYaml}")
    
    with open(args.ArtifactsYaml, "r") as f:
        artifacts_data = yaml.safe_load(f)
    
    # Find the workspace entry matching WorkspaceId
    workspace_entry = None
    for entry in artifacts_data.get("artifacts", []):
        if entry.get("workspaceId") == args.WorkspaceId:
            workspace_entry = entry
            break
    
    if not workspace_entry:
        raise ValueError(f"No artifacts found for workspace {args.WorkspaceId} in YAML")
    
    # Prepare items_in_scope as list of dictionaries
    items_in_scope = workspace_entry.get("items", [])
    print(f"[INFO] Deploying {len(items_in_scope)} items from artifacts YAML")
    
    # Initialize FabricWorkspace
    target_workspace = FabricWorkspace(
        workspace_id=args.WorkspaceId,
        environment=args.Environment,
        repository_directory=args.RepositoryDirectory,
        item_type_in_scope=items_in_scope  # The FabricWorkspace class may need to accept list of dicts
    )

else:
    # Use command-line ItemsInScope
    item_type_in_scope = args.ItemsInScope.split(",") if args.ItemsInScope.lower() != "all" else ["all"]
    target_workspace = FabricWorkspace(
        workspace_id=args.WorkspaceId,
        environment=args.Environment,
        repository_directory=args.RepositoryDirectory,
        item_type_in_scope=item_type_in_scope,
    )

# ---------------------------
# Publish and clean orphan items
# ---------------------------
publish_all_items(target_workspace)
unpublish_all_orphan_items(target_workspace)
