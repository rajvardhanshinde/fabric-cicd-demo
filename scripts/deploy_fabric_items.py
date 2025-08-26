import os
import sys
import argparse
import yaml
import requests

FABRIC_API = "https://api.fabric.microsoft.com/v1/workspaces"

def load_parameters(param_file):
    if not os.path.exists(param_file):
        print(f"❌ Parameter file not found: {param_file}")
        sys.exit(1)

    with open(param_file, "r") as f:
        try:
            params = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"❌ Error parsing {param_file}: {e}")
            sys.exit(1)

    artifacts = params.get("artifacts", [])
    if not artifacts:
        print("⚠️ No artifacts defined in parameter.yml")
    return artifacts


def deploy_artifact(workspace_id, artifact, repo_dir, token):
    # Validate required fields
    for field in ["name", "type", "path"]:
        if field not in artifact:
            print(f"❌ Missing '{field}' in artifact: {artifact}")
            return

    artifact_path = os.path.join(repo_dir, artifact["path"])
    if not os.path.exists(artifact_path):
        print(f"⚠️ Skipping {artifact['name']} — path not found: {artifact_path}")
        return

    print(f"🚀 Deploying {artifact['name']} ({artifact['type']}) from {artifact_path}")

    url = f"{FABRIC_API}/{workspace_id}/items"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "displayName": artifact["name"],
        "type": artifact["type"]
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200 or response.status_code == 201:
        print(f"✅ Deployed {artifact['name']} successfully")
    else:
        print(f"❌ Failed to deploy {artifact['name']}: {response.status_code} {response.text}")


def main():
    parser = argparse.ArgumentParser(description="Deploy Fabric items from repo")
    parser.add_argument("--WorkspaceId", required=True)
    parser.add_argument("--Environment", required=True)
    parser.add_argument("--RepositoryDirectory", required=True)
    parser.add_argument("--ItemsInScope", default="all")
    parser.add_argument("--parameters", required=True)
    args = parser.parse_args()

    token = os.getenv("AZURE_ACCESS_TOKEN")
    if not token:
        print("❌ Missing AZURE_ACCESS_TOKEN. Make sure it is exported in GitHub Actions.")
        sys.exit(1)

    artifacts = load_parameters(args.parameters)

    for artifact in artifacts:
        deploy_artifact(args.WorkspaceId, artifact, args.RepositoryDirectory, token)


if __name__ == "__main__":
    main()
