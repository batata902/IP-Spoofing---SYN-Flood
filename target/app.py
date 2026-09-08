from flask import Flask, request, render_template
from scapy.all import TCP, sniff, IP
import threading
import sqlite3
from contextlib import contextmanager


app = Flask(__name__)


@contextmanager
def db():
	conn = sqlite3.connect('database.db')
	cur = conn.cursor()

	try:
		yield conn, cur
	finally:
		conn.close()


lock = threading.Lock()

def process_tcp(package):

	with lock:
		dont_block = True
		if package.haslayer(IP):
			dont_block = check_ip(package[IP].src)

		if dont_block:
			print (f'[+] TCP Package -> ', package.summary())


def sniff_wire():
	sniff(filter='tcp port 8080', prn=process_tcp)



def check_ip(ip_addr: str) -> bool:
	with db() as (conn, cur):
		query = cur.execute('SELECT recorrencias FROM blacklist WHERE ip=?;', (ip_addr,)).fetchone()

		if not query:
			cur.execute('INSERT INTO blacklist(ip, recorrencias) VALUES (?, 1)', (ip_addr,))
			conn.commit()
			return True

		cur.execute('UPDATE blacklist SET recorrencias=(recorrencias + 1) WHERE ip = ?;', (ip_addr,))
		conn.commit()

		if query[0] > 5000:
			return False

	return True

@app.route('/', methods=['GET'])
def index():
	if not check_ip(request.remote_addr):
		return '<h1>BLOQUEADO</h1>', 403

	return render_template('index.html')


if __name__ == '__main__':
	conn = sqlite3.connect('database.db')
	conn.executescript(open('schema.sql', 'r').read())

	conn.close()

	t = threading.Thread(target=sniff_wire, daemon=True)
	t.start()

	app.run(host='0.0.0.0', port=8080)
