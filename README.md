# devproxy

This project was created to enable developing web applications locally, with
valid HTTPS certificates from Let's Encrypt. It works closely with nginx-proxy
by @jwilder and its Let's Encrypt companion.

Apart from HTTPS validation, it provides a reverse HTTPS proxy so you can easily 
develop from other devices as well.

## Prerequisites

Assume you have nginx-proxy running on your local development machine and you
want to test how your web application behaves when it is served over HTTPS.

The first step is to obtain access to a public-facing Linux system such as a VPS,
or even a Raspberry Pi on your home network with port forwarding enabled. Make sure
you can at least forward port 80/tcp and at least one other port for UDP traffic.

The next step is to obtain a domain name and access to its DNS records. Create a
wildcard A or AAAA record to the IP address that points to your VPS, for example
*.company.dev.

Now, on your VPS, install Docker and WireGuard. Create a WireGuard server config
similar to `server_example.conf`. Make sure the listening port is accessible from
outside.

Enable the WireGuard config. Sometimes this can be done using
`# systemctl enable --now wg-quick@devproxy` (enables and starts
/etc/wireguard/devproxy.conf). 

Install a corresponding WireGuard client config on your local machine and start it
in the same manner.

Check that the two are connected by running `# wg`. The latest handshake should be
less than 2 minutes.

Optionally, the following can be added to root's crontab:

```
* * * * * python3 /home/me/devproxy/cron/update_wg_ip_addresses.py
```

This will automatically safelist IP addresses of WireGuard peers so they can access
the reverse HTTPS proxy.

On your local machine you will need to add whatever domain you are using for
development to `/etc/hosts`, pointing them to `127.0.0.1`. If you use dnsmasq, this
can be achieved more easily by creating `/etc/dnsmasq.d/devproxy.conf`:

```
address=/.my.customer.dev/127.0.0.1
address=/.company.dev/127.0.0.1
address=/.localdev/127.0.0.1
```

When using a VM for development, point to the VM's IP instead of `127.0.0.1` on your
host.

In Windows, Acrylic can be used to rewrite local DNS more elegantly.

## Usage

If you have something running on your VPS on port 80 already, make sure you disable
it or change the port number, e.g. to 57122 (if you choose this port number, HTTPS
validation for nginx-proxy + companion will also work, see `proxy_acme.conf`).

Start devproxy by running `docker compose up -d`. It will now forward requests from
port 80 to any connected WireGuard peer configured in `proxy_acme.conf`, skipping
each host where the requested ACME challenge is not found. On ports 8443, 9443, etc.,
you will be able to access port 443 for each of the peers, granted the IP address is
safelisted.

Add `LETSENCRYPT_HOST=something.company.dev` to the environment of one of your
containers that is in a shared network with nginx-proxy. The Let's Encrypt companion
will pick up on this and request an HTTPS certificate for this hostname. Let's Encrypt
will validate by requesting
`GET http://something.company.dev/.well-known/acme-challenge/<challenge_id>`. This
request is received by devproxy and forwarded to the peers in `proxy_acme.conf`. As
long as your WireGuard tunnel is open, your local nginx-proxy will serve the challenge
through the tunnel for Let's Encrypt to receive, and the companion will receive the
certificate separately.

Externally, you can now access `https://something.company.dev:8443/` and it will proxy
your local machine.

If you weren't using port 443 on this VPS, you can edit `proxy_https.conf` such that
port 443 is used instead of 8443. Make sure you update the `ports` section in
`docker-compose.yml` as well.

The default config accomodates 5 peers. You can share one VPS with your colleagues.

Once you have this running, you'll never have to think about HTTPS certificates again.
