# Incus Exec Module

The `incus_exec` module allows you to execute commands inside Incus instances (containers and Virtual Machines). It wraps the `incus exec` command.

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `name` / `instance` | Yes | - | The name of the instance to execute the command in. |
| `command` | Yes | - | The command to run. Can be a string (parsed via shlex) or a list of arguments. |
| `remote` | No | `local` | The remote server. command. |
| `project` | No | `default` | The project name. |
| `user` | No | - | User ID (int) to run the command as. |
| `group` | No | - | Group ID (int) to run the command as. |
| `cwd` | No | - | Working directory to execute the command in. |
| `env` | No | - | Dictionary of environment variables. |
| `mode` | No | `non-interactive` | Execution mode (`interactive` or `non-interactive`). |

## Examples

### Run a simple command
```yaml
- name: Check uptime
  crystian.incus.incus_exec:
    name: my-web-server
    command: uptime
  register: uptime_result

- debug:
    msg: "{{ uptime_result.stdout }}"
```

### Run complex command sequences
It is often better to use a list for complex arguments.

```yaml
- name: Install packages (alpine)
  crystian.incus.incus_exec:
    name: alpine-01
    command: ['apk', 'add', '--no-cache', 'python3', 'git']
```

### Run as a specific user in a specific directory
```yaml
- name: Run git status as user 1000
  crystian.incus.incus_exec:
    name: dev-container
    command: git status
    cwd: /home/user/repo
    user: 1000
```

### Pass Environment Variables
```yaml
- name: Run script with env
  crystian.incus.incus_exec:
    name: app-01
    command: ./start.sh
    cwd: /opt/app
    env:
      DB_HOST: "db-01"
      DEBUG: "true"
```
