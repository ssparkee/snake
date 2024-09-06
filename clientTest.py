import requests

data = {'message': 'Hello from client'}
response = requests.post('http://localhost:5000/message', json=data)
print(response.json())

SERVER = 'http://localhost:5000'
if __name__ == '__main__':
    response = requests.post(f'{SERVER}/initconnect', json={})  