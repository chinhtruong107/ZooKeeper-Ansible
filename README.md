# ZooKeeper Ansible Automation

Automated deployment of a 3-node Apache ZooKeeper cluster on AWS EC2 using Ansible.

---

## Requirements

- Control node: Ubuntu 22.04 with Ansible installed
- 3 managed nodes: Ubuntu 22.04 EC2 instances
- SSH key pair for EC2 access
- AWS Security Group with ports open: 22, 2181, 2888, 3888

---

## Project Structure

```
ZooKeeper-Ansible/
├── ansible.cfg
├── site.yml                          # Main entry point
├── inventory/
│   └── inventory.ini                 # EC2 hosts
├── group_vars/
│   └── zookeeper.yml                 # Variables
├── playbooks/
│   ├── backup.yml
│   └── restore.yml
└── roles/
    ├── common/                       # Hostname, hosts, chrony, packages
    ├── tuning/                       # File limits, sysctl, swap, logrotate
    ├── zookeeper/                    # Install and configure ZooKeeper
    ├── verify/                       # Health checks
    ├── backup/                       # Backup script and cron job
    └── restore/                      # Restore from backup
```

---

## Configuration

Edit `group_vars/zookeeper.yml`:

```yaml
# SSH
ansible_user: ubuntu
ansible_ssh_private_key_file: "~/.ssh/your-key.pem"

# ZooKeeper
zookeeper_version: "3.9.5"
zookeeper_heap: "256M"
zookeeper_client_port: 2181
zookeeper_quorum_port: 2888
zookeeper_election_port: 3888

# Backup
backup_enabled: true
backup_type: "full"           # full | incremental
backup_frequency: "daily"
backup_retention_days: 7
backup_path: "/backup/zookeeper"

# Restore
restore_enabled: true
restore_type: "full"          # full | single
restore_target: "zk1"        # for single node restore
restore_backup: "20260608_084921"
```

Edit `inventory/inventory.ini`:

```ini
[zookeeper]
zk1 ansible_host=<IP_ZK1>
zk2 ansible_host=<IP_ZK2>
zk3 ansible_host=<IP_ZK3>
```

---

## Usage

### Deploy cluster

```bash
ansible-playbook -i inventory/inventory.ini site.yml
```

### Run backup

```bash
# Deploy backup script and cron job
ansible-playbook -i inventory/inventory.ini playbooks/backup.yml

# Run backup immediately
ansible -i inventory/inventory.ini zookeeper -m shell \
  -a "/usr/local/bin/zookeeper-backup.sh" --become
```

### Run restore

```bash
# 1. Update restore_backup in group_vars/zookeeper.yml
# 2. Run restore
ansible-playbook -i inventory/inventory.ini playbooks/restore.yml
```

---

## Verify Cluster

```bash
# Check all nodes alive
ansible -i inventory/inventory.ini zookeeper \
  -m shell -a "echo ruok | nc 127.0.0.1 2181" --become

# Check leader/follower
ansible -i inventory/inventory.ini zookeeper \
  -m shell -a "echo srvr | nc 127.0.0.1 2181 | grep Mode" --become
```

Expected result:
```
zk1 → follower
zk2 → leader
zk3 → follower
```

---

## Backup Types

| Type | Description |
|------|-------------|
| `full` | Copy all snapshot + transaction log |
| `incremental` | Copy only new transaction logs since last backup |

---

## Restore Types

| Type | Description |
|------|-------------|
| `full` | Restore all 3 nodes |
| `single` | Restore only `restore_target` node |

---

## Roles

| Role | Responsibility |
|------|---------------|
| `common` | Set hostname, /etc/hosts, chrony, install packages |
| `tuning` | File descriptor limits, sysctl, disable swap, logrotate |
| `zookeeper` | Download, install, configure ZooKeeper, create systemd service |
| `verify` | Health checks: ruok, srvr, ports, process |
| `backup` | Deploy backup script, create cron job |
| `restore` | Stop, safety backup, restore data, start, verify |
