Setup python env

```
virtualenv venv
source venv/bin/activate
pip install -r requirments.txt
```
Run the app

```
uvicorn src.main:app
```

To run the test script, open a second terminal, same directory

```
source venv/bin/activate
python test_api.py
```

After a few seconds you should see a response like below

```
<Response [200]>
b'{"puppet_pairs":27}'
```