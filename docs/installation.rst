Installation
============

To install this package::

    pip install pingdom-uptime-report

Configuring, using Pingdom as an example::

    mkdir -p ~/.config
    cat > ~/.config/uptime_report.cfg <<EOF
    [pingdom]
    apikey = ...
    password = ...
    username = user@domain.com
    EOF
