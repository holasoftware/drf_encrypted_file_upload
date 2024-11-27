# Demo DRF Encrypted File Upload
Demo uploading a file and storing the data encrypted using Django Rest Framework.


## Installation
Create a virtualenv:
```
    python -m venv venv
```

Activate virtualenv:
```
    . venv/bin/activate
```

Install the requirements:
```
    pip install -r requirements
```

Create a super user:
```
    python manage.py createsuperuser
```

Start the WSGI server with the environment variable `ENCRYPTION_MASTER_PASSWORD` configured with the master password.

## Architecture
Every file is encrypted with a different key. That key is stored encrypted using a master key in the same django model representing the private document. The master key is derived using a global password provided in an environment variable and a salt. The password is always fixed and it's the value of the environment variable `ENCRYPTION_MASTER_PASSWORD`. The salt is a random value different for every document. That salt is stored also with the data of the document.

For the encryption/decryption, the algorithm AES CTR is used. The stream cypher allows to have the encrypted files with the same size as the original file.

Endpoints:
```
    POST /api/v1/private-document/
    GET /api/v1/private-document/{uuid}/
    PUT /api/v1/private-document/{uuid}/
    PATCH /api/v1/private-document/{uuid}/
    DELETE /api/v1/private-document/{uuid}/
    GET /api/v1/private-document/{uuid}/download/
```

The encrypted files are stored using the django storage API. This allows for example to store all the encrypted files in S3 using a storage backend like `django-s3-storage`, 

## Usage

Create an authorization token `<ACCESS TOKEN>` for a user, for example `root`:
```
    python manage.py drf_create_token root
```

You can also create a token using the admin panel visiting. The admin panel is located in this path `/admin/`.

Run the WSGI server, exporting the master password in the environment variable `ENCRYPTION_MASTER_PASSWORD`. For example:
```
    ENCRYPTION_MASTER_PASSWORD=<YOUR PASSWORD> python manage.py runserver
```
or
```
    export ENCRYPTION_MASTER_PASSWORD=<YOUR PASSWORD>
    python manage.py runserver
```

Create a test file:
```
    echo 'this is a test' > test.txt
```

Upload the test document with this curl command:
```
    curl -X POST -H 'Authorization: Token <ACCESS TOKEN>' -F 'file=@test.txt' -F 'title=title of the document' http://127.0.0.1:8000/api/v1/private-document/
```

The document UUID is returned in the previous response. Using the document UUID, we can download the file unencrypted:
```
    curl -X GET -H 'Authorization: Token <ACCESS TOKEN>' http://127.0.0.1:8000/api/v1/private-document/<DOCUMENT UUID>
```