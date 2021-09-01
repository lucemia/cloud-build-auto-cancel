from google.cloud.devtools import cloudbuild_v1
from collections import defaultdict

PROJECT_ID = None

def main(*args, **kwargs):
    client = cloudbuild_v1.services.cloud_build.CloudBuildClient()

    # REF: https://stackoverflow.com/questions/60688977/google-cloud-build-pypi-400-errors
    r = cloudbuild_v1.types.ListBuildsRequest(
        project_id=PROJECT_ID, filter='status="WORKING"'
    )

    resp = client.list_builds(r)

    # NOTE: test here
    # https://cloud.google.com/build/docs/api/reference/rest/v1/projects.builds/get

    CACHE = defaultdict(list)

    for build in resp:
        if "TAG_NAME" in build.substitutions:
            # NOTE: don't cancel tag build
            continue

        assert "BRANCH_NAME" in build.substitutions, build

        branch = build.substitutions["BRANCH_NAME"]
        repo = build.substitutions["REPO_NAME"]

        CACHE[(repo, branch)].append(build)

    for (repo, branch), builds in CACHE.items():
        if len(builds) == 1:
            continue

        builds = sorted(builds, key=lambda build: build.create_time)

        for build in builds[:-1]:
            print(f"cancel build {build.id}")
            client.cancel_build(project_id="living-bio", id=build.id)


if __name__ == "__main__":
    main()
