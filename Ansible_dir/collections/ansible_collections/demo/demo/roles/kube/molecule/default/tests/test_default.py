import os
import testinfra.utils.ansible_runner
"""Role testing files using testinfra."""

def test_hosts_file(host):
    """Validate /etc/hosts file."""
    f = host.file("/etc/hosts")

    assert f.exists
    assert f.user == "root"
    assert f.group == "root"

def test_crio_installed(host):
    assert host.package("cri-o").is_installed

def test_kube_packages_installed(host):
    for pkg in ["kubelet", "kubeadm", "kubectl"]:
        assert host.package(pkg).is_installed

def test_kubelet_service_enabled(host):
    service = host.service("kubelet")
    assert service.is_enabled
