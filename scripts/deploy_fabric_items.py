import os
import yaml
import requests
import argparse
import sys

def load_parameters(path):
    """Load YAML config for artifacts"""
    with open(path, "r") as f:
        return yaml.safe_load(f)

def deploy_artifact(workspace_id, artifact_path, artifact_type, token):
    """Deploy artifact to Fabric workspace"""
    if not os.path.exists(artifact_path):
        print(f"⚠️ Skipping {artifact_path}, path not found")
        return

    print(f"📤 Deploying {artifact_path} as {artifact_type} to workspace {workspace_id}")

    # NOTE: Adjust endpoint for Fabric API
    url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/artifacts"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "name": os.path.basename(artifact_path),
        "type": artifact_type,
        "path": artifact_path
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code in [200, 201]:
        print(f"✅ Successfully deployed {artifact_path}")
    else:
        print(f"❌ Failed to deploy {artifact_path}: {response.status_code} {response.text}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--WorkspaceId", required=True)
    parser.add_argument("--Environment", required=True)
    parser.add_argument("--RepositoryDirectory", required=True)
    parser.add_argument("--ItemsInScope", default="all")
    parser.add_argument("--parameters", default="parameter.yml")
    args = parser.parse_args()

    workspace_id = args.WorkspaceId
    repo_dir = args.RepositoryDirectory

    # Token from Azure login
    token = os.environ.get("AZURE_ACCESS_TOKEN")
    if not token:
        print("❌ Missing AZURE_ACCESS_TOKEN in environment")
        sys.exit(1)

    params = load_parameters(args.parameters)
    artifacts = params.get("artifacts", [])

    for artifact in artifacts:
        artifact_path = os.path.join(repo_dir, artifact["path"])
        deploy_artifact(workspace_id, artifact_path, artifact["type"], token)

if __name__ == "__main__":
    main()
