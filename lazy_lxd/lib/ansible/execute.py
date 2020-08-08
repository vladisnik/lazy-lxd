import os
import subprocess
import shlex
import json

from halo import Halo


def run_ansible_playbook(self, playbook: str) -> tuple:
    """
    Running the Ansible playbook.
    Utility ansible-playbook is used for that.
    Receiving exit code, stdout and stderr from executed process.
    Stdout presented as JSON.

    Args:
        playbook (str): Path to Ansible playbook which needs to run.

    Returns:
        tuple: Result of running playbook.
               Exit code, stdout message and error if occurred and executed command.
    """

    playbook_full_path = os.path.join(self.playbooks_path, playbook)

    env = os.environ.copy()
    env.update({
        'ANSIBLE_SSH_ARGS': '-o IdentitiesOnly=yes',
        'ANSIBLE_REMOTE_USER': 'root',
        'ANSIBLE_PRIVATE_KEY_FILE': self.ssh_key,
        'ANSIBLE_STDOUT_CALLBACK': 'json'
    })
    cmd = shlex.split(f'ansible-playbook -i {self.container_host}, {playbook_full_path}')

    process = subprocess.Popen(
        cmd, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # build command with argument from env
    shell_cmd = (
        f"ANSIBLE_SSH_ARGS='{env['ANSIBLE_SSH_ARGS']}' {' '.join(cmd[:3])} "
        f"--private-key {self.ssh_key} -u {env['ANSIBLE_REMOTE_USER']} {cmd[-1]}"
    )

    self._log.debug(f"Playbook will executing by command: {shell_cmd}")
    with Halo(text=f"Running playbook {playbook}...", spinner="dots12", color="blue"):
        out, err = process.communicate()

    if len(out.decode()) > 0:
        out = json.loads(out.decode())

    return (process.returncode, out, err.decode(), shell_cmd)
