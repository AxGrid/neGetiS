---
layout: doc.html
morph: doc
title: "Быстрый старт"
anchors:
    - title: Вступление 
    - title: Установка
      children:
        - Требования
    - title: Первый сайт
---

## Вступление

Начиная работать с *negetis* вы будите постипенно осваивать его множиственные возможности. 
Просмотрев всю документацию вы поймете насколько это масштабный инструмент для создания статичных сайтов.


## Требования

Negetis разработан на языке програмирования python.
для функционирования вам необходим *python* версии >= 3.5


## Установка

#### OSX

```shell
pip install negetis
``` 

#### Linux

```shell
pip install negetis
``` 

#### WINDOWS
```shell
no idea now)
``` 


После этого он доступен в командной строке как `negetis`.

Для проверки выполните: 

```shell
negetis version
```

---SPLIT---


## Первый сайт

Для того чтоб просто создать сайт выполните:

```shell
negetis newsite my-first-site
cd ./my-first-site
```

Теперь на нужно добавить тему. 

_Более подробно про создание и добавлении тем можно прочитать тут:_

```shell
negetis addtheme basic
```

Можем смотреть что получилось:

```shell
negetis server -D
```

Откроем браузер [http://localhost:8888/](http://localhost:8888/)

Создадим первый пост

```shell
negetis post my-first-post
nano ./content/my-first-post.md
```

Обновим страницу, посмотрим что получилось: [http://localhost:8888/](http://localhost:8888/)