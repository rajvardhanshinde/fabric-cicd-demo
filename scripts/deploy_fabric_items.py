import os
import yaml
import requests
import argparse
import sys
import glob

def load_parameters(path):
    """Load YAML config for artifacts"""
    with open(path, "r") as f:
        return yaml.safe_load(f)

def get_api_url(workspace_id, artifact_type):
    """Return Fabric API endpoint for the artifact type"""
    base = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}"
    if artifact_type == "Notebook":
        return f"{base}/notebooks/import"
    elif artifact_type == "Report":
        return f"{base}/reports/import"
    elif artifact_type == "SemanticModel":
        return f"{base}/semanticModels/import"
    else:
        raise ValueError(f"❌ Unsupported artifact type: {artifact_type}")

def deploy_artifact(workspace_id, file_path, artifact_type, token):
    """Deploy single artifact file to Fabric workspace"""
    print(f"📤 Deploying {file_path} as {artifact_type} to workspace {workspace_id}")

    url = get_api_url(workspace_id, artifact_type)
    headers = {
        "Authorization": f"Bearer {token}"
    }

    files = {
        "file": (os.path.basename(file_path), open(file_path, "rb"))
    }

    response = requests.post(url, headers=headers, files=files)

    if response.status_code in [200, 201]:
        print(f"✅ Successfully deployed {file_path}")
    else:
        print(f"❌ Failed to deploy {file_path}")
        print(f"➡️ Status: {response.status_code}")
        print(f"➡️ Response: {response.text}")

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
        artifact_dir = os.path.join(repo_dir, artifact["path"])
        if not os.path.exists(artifact_dir):
            print(f"⚠️ Skipping {artifact_dir}, path not found")
            continue

        # Deploy all files under this artifact folder
        for file_path in glob.glob(os.path.join(artifact_dir, "**"), recursive=True):
            if os.path.isfile(file_path):
                deploy_artifact(workspace_id, file_path, artifact["type"], token)

if __name__ == "__main__":
    main()
