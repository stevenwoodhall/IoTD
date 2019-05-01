def count_blocked_domains():
    try:
        blocked_domains = sum(1 for line in open(
            '/opt/iotd/app/dns/hosts-blocklists/domains.txt'))
        return blocked_domains
    except Exception:
        return 0
