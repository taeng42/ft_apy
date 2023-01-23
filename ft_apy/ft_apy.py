import urllib3
import json
from time import sleep
import time

ENDPOINT = 'https://api.intra.42.fr'

class HttpRequest(object):
	def __init__(self, target: str, session, **kwargs):
		self.url = f"{ENDPOINT}{target}"
		self.session = session
		if "filter" in kwargs:
			self.filter = kwargs["filter"]
		else:
			self.filter = {}
		if "page" in kwargs:
			self.page = kwargs["page"]
		else:
			self.page = {"size": 100, "number": 1}  # 100 is MAX size
		if "sort" in kwargs:
			self.sort = kwargs["sort"]
		else:
			self.sort = ""
		if "range" in kwargs:
			self.range = kwargs["range"]
		else:
			self.range = {}

	# Needs to handle kwargs into different parameters
	def parse_params(self):
		if self.filter:
			filtering = '&'.join([f"filter[{key}]={value}" for key, value in self.filter.items()]) + '&'
		else:
			filtering = ""
		page = '&'.join([f"page[{key}]={value}" for key, value in self.page.items()])
		parsed_param = filtering + page
		if self.sort:
			parsed_param += f"&sort={self.sort}"
		if self.range:
			ranges = '&'.join([f"range[{key}]={value}" for key, value in self.range.items()])
		else:
			ranges = ""
		if self.range:
			parsed_param = parsed_param + '&' + ranges

		return f"?{parsed_param}"

	def get(self):
		try:
			resp = self.session.request("GET", self.url + self.parse_params())
		except urllib3.exceptions.HTTPError as e:
			print(e)
			return {}
		if 400 <= resp.status < 600:
			print(resp.status)
			print(resp.data.decode('utf-8'))
			return {}
		return json.loads(resp.data.decode('utf-8'))

	def put(self, data: json):
		try:
			body = json.dumps(data).encode('utf-8')
			headers = {
				'Authorization': self.session.headers['Authorization'],
				'Content-Type': "application/json"
			}
			resp = self.session.request("PUT", self.url, body=body, headers=headers)
		except urllib3.exceptions.HTTPError as e:
			print(e)
			return {}
		if 400 <= resp.status < 600:
			print(resp.status)
			print(resp.data.decode('utf-8'))
			return {}
		return resp

	def post(self, data: json):
		try:
			body = json.dumps(data).encode('utf-8')
			headers = {
				'Authorization': self.session.headers['Authorization'],
				'Content-Type': "application/json"
			}
			resp = self.session.request("POST", self.url, body=body, headers=headers)
		except urllib3.exceptions.HTTPError as e:
			print(e)
			return {}
		if 400 <= resp.status < 600:
			print(resp.status)
			print(resp.data.decode('utf-8'))
			return {}
		return resp

	def patch(self, data):
		try:
			body = json.dumps(data).encode('utf-8')
			headers = {
				'Authorization': self.session.headers['Authorization'],
				'Content-Type': "application/json"
			}
			resp = self.session.request("PATCH", self.url, body=body, headers=headers)
		except urllib3.exceptions.HTTPError as e:
			print(e)
			return {}
		if 400 <= resp.status < 600:
			print(resp.status)
			print(resp.data.decode('utf-8'))
			return {}
		return resp

	def delete(self):
		try:
			resp = self.session.request("DELETE", self.url)
		except urllib3.exceptions.HTTPError as e:
			print(e)
			return {}
		if 400 <= resp.status < 500:
			print(resp.status)
			print(resp.data.decode('utf-8'))
			return {}
		return resp


class Api(object):
	def __init__(self, uid: str, secret: str, req_code: str = None, redirect: str = None, token: str = None):
		self.uid = uid
		self.secret = secret
		self.req_code = req_code
		self.expired_at = None
		self.__token = token
		self.redirect = redirect
		self.session = urllib3.PoolManager()
		if self.__token is None:
			self.__token = self.authenticate()

		self.session.headers.update({"Authorization": f"Bearer {self.__token}"})
		self.call_cnt = 0

	def authenticate(self):
		self.session.clear()
		if self.req_code:
			# 3 legged authentication
			auth_data = {
				"grant_type": "authorization_code",
				"client_id": self.uid,
				"client_secret": self.secret,
				"code": self.req_code,
				"redirect_uri": self.redirect
			}
		else:
			# 2 legged authentication
			auth_data = {
				"grant_type": "client_credentials",
				"client_id": self.uid,
				"scope": "public profile projects tig elearning forum",
				"client_secret": self.secret
			}
		resp = self.session.request("POST", f"{ENDPOINT}/oauth/token", fields=auth_data)
		print(resp.status)
		parsed_resp = json.loads(resp.data.decode('utf-8'))
		print("token generated. Expires in:", parsed_resp["expires_in"], "seconds")
		self.expired_at = int(time.time()) + parsed_resp["expires_in"]
		return parsed_resp["access_token"]


	def path(self, path: str, **kwargs):
		cur = int(time.time())
		if self.expired_at <= cur + 1:  # 1초 안에 이 토큰의 수명이 끝난다면
			# 1초를 기다리고 재발급한다.
			print("[🔒💣] TOKEN expires in 1 seconds")
			print("[⏳] Sleep 1 seconds . . ")
			sleep(1.0)
			print("[🔐] RELOAD TOKEN !!")
			self.session = urllib3.PoolManager()
			self.__token = self.authenticate()
			self.session.headers.update({"Authorization": f"Bearer {self.__token}"})
		target = f"/v2/{path}"
		self.call_cnt += 1
		if self.call_cnt % 8 == 0:
			sleep(0.3)
		return HttpRequest(target, self.session, **kwargs)

	def print_token(self):
		print(type(self.__token))
		print(self.__token)
