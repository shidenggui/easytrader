 
**Python installation**

* Install windows python3 from python.org

** Python module installation**

* pip install -r requirements.txt
* pip install Pillow
* pip install pytesseract

 **Tesseract installation**

* wget https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/pytesser/pytesser_v0.0.1.zip
* unzip pytesser_v0.0.1.zip
* Put tesseract.exe tessdata\ under C:\Users\xxxx\AppData\Local\Programs\Python\Python35\Scripts\
 Config json file like gf.json
* Open https://trade.gf.com.cn in IE
* Input Account and Password (select 'save account')
* Login (for creating 'userId' Cookie)
* Logout
* Input Account and Password
* F12 | Console
* Copy userId from Cookie and paste into gf.json | username
* var e=document.getElementById("SecurePassword")
* e.GetPassword()
* Copy password and paste into gf.json | password
 Run
* python cli.py --use gf --prepare gf.json
