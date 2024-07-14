<h1 align="center">NeulBom Backend Project</h1>
<p align="center">
  <img alt="" src="assets/logo.png" style="width: 256px; height: 256px;" border="9999px">
</p>
<h3 align="center">This is Research version written by Leader, <a href="https://github.com/ZerOneDeveloper">ChanWoo Song</a> with <a href="https://fastapi.tiangolo.com/">FastAPI</a></h3>

## 1. Project Structure
```
├── README.md
├── app.py
├── setup.py
├── routes
│   ├── meal
│   │   ├── __init__.py
│   │   ├── route.py
│   ├── user
│   │   ├── __init__.py
│   │   ├── route.py
│   ├── board
│   │   ├── __init__.py
│   │   ├── route.py
│   ├── auth
│   │   ├── __init__.py
│   │   ├── route.py
├── test
│   ├── mealList
│   ├── temp.py
│   ├── testAuthCode.py
│   ├── testMealConverter.py
│   ├── testRunEmail.py
├── utilities
│   ├── __init__.py
│   ├── config.py
│   ├── emailSender.py
│   ├── http.py
│   ├── logger.py
│   ├── mealJSONConverter.py
│   ├── security.py
│   ├── userGenerator.py
│   ├── database
│   │   ├── func.py
├── config.ini
├── config.example.ini
├── requirements.txt
```

## 2. How to run
1. Install python3 and pip3
2. Install requirements
3. Fill `config.ini` like `config.example.ini`
- HOST value is your server ip address
- PORT value is your server port
- DEBUG value is your server debug mode (True or False)
4. Run app.py with next command
```
$ pip3 install -U -r requirements.txt
$ python3 app.py
```


## 3. Issues?
- If your issue is the issue of the scrypt package, please follow.
1. [Windows, Install OpenSSL Package](https://slproweb.com/products/Win32OpenSSL.html)
2. MacOS, Install OpenSSL Package
```
$ brew install openssl
$ export CFLAGS="-I$(brew --prefix openssl)/include $CFLAGS"
$ export LDFLAGS="-L$(brew --prefix openssl)/lib $LDFLAGS"
$ pip3 install scrypt
```
3. Debian and Ubuntu
```
$ sudo apt-get install build-essential libssl-dev python-dev
$ pip3 install scrypt
```
4. Fedora and RHEL-derivatives
```
$ sudo yum install gcc openssl-devel python-devel
$ pip3 install scrypt
```
