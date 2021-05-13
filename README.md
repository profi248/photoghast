# photoghast
photoghast is a web application to convenintly view and organize your photo library. It works by indexing a folder with photos (subfolders automatically create albums) and saving all metadata including thumbnails in a database. After indexing your photos, log in to the website and view your photos in a stream from newest to oldest, browse by albums or check out places where you took photos. Places are automatically indexed if photos have GPS tags.

## Dependencies
This application also needs `exiftool` to be installed and accessible in system `PATH`.  SQLite is also required.

On Fedora, these depedencies (and others necessary to install Python modules) can be installed by running the following command.
```
sudo dnf install perl-Image-ExifTool sqlite3 gcc libffi-devel python-devel
```

Python depedencies are managed with `pip` and `virtualenv`. Required packages are in `requirements.txt`. Create a `virutalenv` and install dependencies with these commands below.
```
python -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
## Usage
Configure settings in `utils/config.py`, especially the absolute path 
to folder with pictures that you want to index and display.

Preparing for running (after installing all dependencies):
```
cd app
export PYTHONPATH=$PYTHONPATH:$(pwd)
python utils/create_db.py
```
Indexing all photos in the specified folder and starting the app:
```
python indexer/indexer.py
python web/main.py
```
Default credentials for the web UI are `admin` / `pythonrocks` (specified in config). 

## Unit tests
Running unit tests:
```
python -m unittest discover -s tests
```

## Folder structure
```
.
├── README.md
├── app
│   ├── indexer
│   │   ├── indexer.py
│   │   └── thumbnail.py
│   ├── tests
│   │   ├── __init__.py
│   │   ├── test_thumbnail.py
│   │   └── test_user.py
│   ├── thumnail_test.ipynb
│   ├── utils
│   │   ├── __init__.py
│   │   ├── common.py
│   │   ├── config.py
│   │   ├── create_db.py
│   │   └── db_models.py
│   └── web
│       ├── forms.py
│       ├── main.py
│       ├── static
│       ├── templates
│       │   ├── albums.html
│       │   ├── base.html
│       │   ├── index.html
│       │   ├── library.html
│       │   ├── login.html
│       │   └── places.html
│       └── user_manager.py
└── requirements.txt
```