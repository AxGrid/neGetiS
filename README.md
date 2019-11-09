neGetiS
=======

Static site generator


Instalation
-----------

```
pip install negetis 
```

Usage
-----

```
negetis newsite my-first-site
cd ./my-first-site
negetis addtheme basic
negetis post my-first-post
nano ./content/posts/my-first-post.md
negetis server -D
```

open browser at `http://localhost:8888/`



Develop
-------

Requirements:

* poetry


```
git clone https://github.com/AxGrid/neGetiS.git
cd ./neGetiS
poetry install
```