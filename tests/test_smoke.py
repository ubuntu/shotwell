import yaml
import subprocess
import time
import pytest


def test_install():
    with open("snap/snapcraft.yaml") as file:
        snapcraft = yaml.safe_load(file)

        subprocess.run(
            f"sudo snap install ./{snapcraft['name']}_*_amd64.snap --devmode",
            check=True,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )


@pytest.mark.run(after="test_install")
def test_all_apps():
    with open("snap/snapcraft.yaml") as file:
        snapcraft = yaml.safe_load(file)

        override = {}

        skip = []

        for app, data in snapcraft["apps"].items():
            if not bool(data.get("daemon")) and app not in skip:
                command = (
                    app if snapcraft["name"] == app else f"{snapcraft['name']}.{app}"
                )

                print(f"Testing {command}....")
                subprocess.run(
                    f"{command} {override.get(app, '--help')}".split(),
                    check=True,
                )


@pytest.mark.run(after="test_install")
def test_all_services():
    with open("snap/snapcraft.yaml") as file:
        snapcraft = yaml.safe_load(file)

        skip = []

        for app, data in snapcraft["apps"].items():
            if bool(data.get("daemon")) and app not in skip:
                print(f"\nTesting {snapcraft['name']}.{app} service....")
                subprocess.run(
                    f"sudo snap start {snapcraft['name']}.{app}".split(), check=True
                )
                time.sleep(5)
                service = subprocess.run(
                    f"snap services {snapcraft['name']}.{app}".split(),
                    check=True,
                    capture_output=True,
                )
                subprocess.run(f"sudo snap stop {snapcraft['name']}.{app}".split())

                assert "active" in str(service.stdout)
