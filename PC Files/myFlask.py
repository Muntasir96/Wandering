from flask import Flask

import sys
str = sys.argv[1]
pn = 6991


app = Flask(__name__)

@app.route("/") # opens up a local server
def hello():
	return str


ip = "192.168.1.105" # ipv4 address of the PC



if __name__ == '__main__':
	app.run(host = ip,port=pn)
