from autotest.client import utils
from virttest import utils_test


def run_nic_promisc(test, params, env):
    """
    Test nic driver in promisc mode:

    1) Boot up a VM.
    2) Repeatedly enable/disable promiscuous mode in guest.
    3) Transfer file from host to guest, and from guest to host in the same time

    @param test: KVM test object.
    @param params: Dictionary with the test parameters.
    @param env: Dictionary with test environment.
    """
    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()
    timeout = int(params.get("login_timeout", 360))
    session_serial = vm.wait_for_serial_login(timeout=timeout)

    ethname = utils_test.get_linux_ifname(session_serial,
                                              vm.get_mac_address(0))

    try:
        transfer_thread = utils.InterruptedThread(
                                               utils_test.run_file_transfer,
                                               (test, params, env))
        transfer_thread.start()
        while transfer_thread.isAlive():
            session_serial.cmd("ip link set %s promisc on" % ethname)
            session_serial.cmd("ip link set %s promisc off" % ethname)
    except Exception:
        transfer_thread.join(suppress_exception=True)
        raise
    else:
        transfer_thread.join()
