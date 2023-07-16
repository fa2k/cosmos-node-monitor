# cosmos-node-monitor

This is a simple script to send alerts for a node based on Cosmos SDK in case
the node is not working.

Example command line to monitor a Cosmos node at IP address 192.168.1.19.

    python monitor.py \
        --node_host=192.168.1.19 \
        --smtp_server=smtp.example.com \
        --to_email=staff@example.com \
        --smtp_username=monitoring \
        --smtp_password=niceTry


Note that to monitor hosts other than localhost, you need to enable remote RPC
access. It is in the app's config directory, Tendermint config file.

    .<app>/config/config.toml

Please note, however, that enabling RPC access on the public Internet has security
implications. Don't enable remote RPC unless you understand those (I don't, and have
only enabled LAN access in the firewall).
