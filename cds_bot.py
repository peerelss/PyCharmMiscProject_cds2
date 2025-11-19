from utils.utils_k import ping_ip
import utils.utils_k
ips = utils.utils_k.txt_2_list('ips.txt')
ip_offline = []
for ip in ips:
    if not ping_ip(ip):
        print(ip)
        ip_offline.append(ip)