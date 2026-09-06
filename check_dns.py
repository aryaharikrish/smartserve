import dns.resolver

clusters = [
    "cluster0.pjkmtee.mongodb.net",
    "cluster0.orogvax.mongodb.net",
    "cluster0.0t54vmr.mongodb.net"
]

with open("dns_res.txt", "w") as out:
    for c in clusters:
        srv_name = f"_mongodb._tcp.{c}"
        try:
            answers = dns.resolver.resolve(srv_name, 'SRV')
            out.write(f"EXISTS: {c} -> {[str(r.target) for r in answers]}\n")
        except Exception as e:
            out.write(f"NOT FOUND: {c} ({type(e).__name__}: {e})\n")
