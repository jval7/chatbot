cd temporal_pkg
pip install -r requirements.txt --platform=manylinux2014_x86_64 --only-binary=:all: --target ./python/lib/python3.11/site-packages/
zip -r layer.zip python