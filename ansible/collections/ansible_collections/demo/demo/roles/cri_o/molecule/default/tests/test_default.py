"""Role testing files using testinfra."""


def test_hosts_file(host):
    """Validate /etc/hosts file."""
    f = host.file("/etc/hosts")

    assert f.exists
    assert f.user == "root"
    assert f.group == "root"

#check installed crio
def test_crio_package_installed(host):
    assert host.package("cri-o").is_installed

def test_crio_service_running(host):
    service = host.service("crio")
    assert service.is_running
    assert service.is_enabled

#check socket
def test_crio_socket_exists(host):
    f = host.file("/var/run/crio/crio.sock")
    assert f.exists
    assert f.is_socket
