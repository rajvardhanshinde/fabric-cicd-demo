from fabric_cicd import FabricWorkspace, publish_all_items, unpublish_all_orphan_items
import argparse

parser = argparse.ArgumentParser(description='Deploy items to Fabric')
parser.add_argument('--WorkspaceId', type=str, required=True)
parser.add_argument('--Environment', type=str, required=True)
parser.add_argument('--RepositoryDirectory', type=str, required=True)
parser.add_argument('--ItemsInScope', type=str, required=True)
args = parser.parse_args()

# Split ItemsInScope into list
item_type_in_scope = args.ItemsInScope.split(",")

# Define target workspace
target_workspace = FabricWorkspace(
    workspace_id=args.WorkspaceId,
    environment=args.Environment,
    repository_directory=args.RepositoryDirectory,
    item_type_in_scope=item_type_in_scope,
)

# Publish and clean orphan items
publish_all_items(target_workspace)
unpublish_all_orphan_items(target_workspace)

