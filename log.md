# 2020/5/4

本格的に動画の視聴を開始。
仮想環境(django_udemy)にdjangoなどをインストールした。
djnagoのバージョンは3.0.5

# 1 - アプリ作成

## プロジェクトの作成

```terminal
django-admin startproject [app name]
```

すると以下のようなフォルダが作られる。

```
first_app/
 |
 |-- first_app/
 |       |--  __init.py など
 |       |-- settings.py
 |       |-- urls.py
 |       |-- wsgi.py (web service gateway interface)
 |       
 |-- manage.py
```

## サーバーの起動
```terminal
python manage.py runserver
```

## 初期設定
settings.pyの言語設定を変える
```python
LANGUAGE_CODE = 'ja'
TIME_ZONE = 'Asia/Tokyo'
```

## マイグレーション
```terminal
python manage.py migtrate
```

## アプリケーションの作成
```terminal
python manage.py startapp [app name]
# 基本的には posts のような複数形にする
```

新たに posts というフォルダが作成される。
アプリケーションの存在をプロジェクトに伝えるために`settings.py`の33行目くらいにある`INSTALLED_APPS`の最後に`posts`を追加します。

```
tdl/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'posts', # これを書き加える udemyではposts/apps.pyを参照してposts.apps.PostConfigとしていた。
]
```

> Django 1.9 からこの作業は不要になったらしいです。tdlsite/apps.py ファイルから自動検出してくれます。

## Hello World を表示する
posts/views.py をいじる

処理の流れ
first_app/urls.py -> posts/urls.py -> views.index

`first_app/urls.py`のurlpatternsを追加する。

```python:first_app/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls), # adminのサイト
    path('posts/',include('posts.urls')),
]
```

`posts/urls.py`を作成し、urlpatternsを作成する。

```python:posts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
```

url で `8000/posts/` とすると、 `first_app/urls.py` の情報を見に行く。
すると、`posts/urls.py`に飛ばされる。
`posts/urls.py`では viewのindexを見に行くように定義されている。


## テンプレートファイルを追加する

view.pyからhtmlを読みに行くようにする。
`posts`のなかに `templates/posts/index.html` をつくる。
djangoのルールでアプリケーションと同じ名前のフォルダ名を作る必要がある。

```python:view.py
from django.shortcuts import render

def index(request):
    return render(request,'posts/index.html')
```

これで
クライアントのリクエスト -> ルーティング(urls.py) -> View(views.py) -> テンプレート(html)
の一連の流れができた。

次はDBに接続するぞ！

------

# 2 - モデル作成

## モデルを定義

### 1. models.pyをいじる(modelの作成)

```python:models.py
from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=255)
    published_at = models.DateTimeField()
    image = models.ImageField(upload_to='media/')
    body = models.TextField()
```

### 2. マイグレーションファイルの作成

```terminal
python manage.py makemigrations
```

modelsを新たに作ったり更新した時にその差分を投入するためのファイルを生成する。

`first_app/posts/migrations/0001_initial.py`
このようなファイルが生成される。

### 3. マイグレーション

マイグレーションファイルを適用してデータベースを更新する処理。

```terminal
python manage.py migrate
```

本当にデータがあるかはコマンドラインに接続する必要がある。

```terminal
sqlite3 db.sqlite3
```

# 3 - 管理サイト

## adminページをいじる

superuser をつくる
```terminal
python manage.py createsuperuser
```

管理画面にログインする

admin.pyを編集して記事の投稿の管理画面を作る

```python:first_app/posts/admin.py
from django.contrib import admin
from .models import Post

admin.site.register(Post)
```

これでもう一度管理画面にアクセスするとPostsというテーブルが作成されている
実際にPostsのモデルで定義した記事のCRUDができる！

## 投稿のタイトルが見えるようにする

`__str__` メソッドをPostに追加する

```python:first_app/posts/models.py
    def __str__(self):
        return self.title
```

## 記事一覧を表示する

Template Engine
変数にhtmlを渡して動的に値を埋め込んだページを作るためのもの
Django純正とJinja2の２種類がある。

bodyの中にテンプレートを埋め込んだ

```html:first_app/posts/templates/posts/index.html
<h1>投稿一覧</h1>
<h2>最新の投稿</h2>
{% for post in posts.all %}
<p>
  {{ post.title }}
</p>
{% endfor %}
```

modelsとviewsを改良していくことでpostsのページが改良されていく...

## statis なデータを扱う
呼び出すurlとフォルダ指定

urls.pyを以下のように書き換える

```python:first_app/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls), # adminのサイト
    path('posts/',include('posts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

first_app/settings.py

```
STATIC_URL = '/static/'
# この 2行を加える
MEDIA_URL = '/pics/'
MEDIA_ROOT = BASE_DIR
```

ブラウザから「ページのソースを確認」で画像のurlなどを確認できる

## 詳細ページの作成

`python:first_app/posts/urls.py` の ururlpatternsに

```
path('<int:post_id>', views.detail, name='detail' ),
```

を追加。view.pyに detial メソッドを追加する。 url の変数名はメソッドの引数に対応している。

```
def detail(request, post_id):
    post = Post.objects.get(pk=post_id)
    return render(request, 'posts/detail.html', {'post': post})
```

最後に詳細ページのテンプレートを作成 `html:detail.html` を参照。

## 404ページの設定

views で 先頭の行のインポートに`get_object_or_404`を追加。
detailメソッドのpostの部分を
```
post = get_object_or_404(Post, pk=post_id)
```
とする。

## 投稿一覧から詳細へのリンクを取得する

index.htmlにリンクを作る

```html:index.html
<p><a href="{% url 'detail' post.id %}">{{ post.title }}</a></p>
```

テンプレータグのurl内では変数を渡せる。
1番目の変数 'detail' は urls.py の ururlpatterns の name に対応している。

## bootstrapの適用

写真の幅などのUI周りをきれいにする。

* css
* jQuery
* BootStrap.js

bootstrapのサイトからソースコードを拝借して自分のhtmlに貼り付ける
https://getbootstrap.com/docs/4.4/getting-started/introduction/
Starter Temlateの一部とcomponentsのnav barを使う

ナビゲーションバーがついて少し見た目が良くなった

## 写真のレスポンシブ対応

imgのタグの中に
```
class="img-fluid"
```
を追加する。

### 静的ファイルは"static"フォルダに
settings.py に
```
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
```
を追加。

`first_app/posts/static/posts/anzu_slack2.png` 画像ファイルをstaticのなかに設置

画像が読み込まれないときはコマンドラインで
```terminal
python manage.py collectstatic
```
を実行する


# 4 - AWS



AWSでEC2インスタンスを作成したらターミナルからsshで接続する。その時にはawsで秘密鍵をダウンロードする必要がある。
ダウンロードしたら権限を変更しておく。

```terminal
chmod 400 django_udemy.pem
ssh -i "django_udemy.pem" ubuntu@ec2-13-114-88-188.ap-northeast-1.compute.amazonaws.com
```

aws上のubuntuに接続したら設定や必要なもののインストールをする。

```
sudo apt-get update
sudo apt-get install
sudo apt-get install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx
```

終わったらPostgreSQLの設定をする。

```
sudo -u postgres psql
```

```
postgres=#
```
と出てきたらコマンドを入力する。

```
postgres=# create database firstapp; # firstapp というDBを作成
CREATE DATABASE
postgres=# create user firstappuser with password 'qwert'; # 新しいユーザーの作成
CREATE ROLE
postgres=# alter role firstappuser set client_encoding to 'utf8'; # 日本語を使えるようにする
ALTER ROLE
postgres=# alter role firstappuser set default_transaction_isolation to 'read commited'; # 権限の変更1回目はtypoしている
ERROR:  invalid value for parameter "default_transaction_isolation": "read commited"
HINT:  Available values: serializable, repeatable read, read committed, read uncommitted.
postgres=# alter role firstappuser set default_transaction_isolation to 'read committed';
ALTER ROLE
postgres=# alter role firstappuser set timezone to 'UTC+9'; # タイムゾーンの変更
ALTER ROLE
postgres=# grant all privileges on database firstapp to firstappuser; 権限の設定
GRANT
postgres=# \q # PostgreSQLを終了
ubuntu@ip-172-31-47-18:~$
```

## virtualenv で仮想環境を構築する

ubuntuに接続してvirtualenvを導入
```
sudo -H pip3 install --upgrade pip
sudo -H pip3 install virtualenv
```

```
ubuntu@ip-172-31-47-18:~$ pwd
/home/ubuntu

ubuntu@ip-172-31-47-18:~$ virtualenv django_udemy # 仮想環境の作成

ubuntu@ip-172-31-47-18:~$ ls django_udemy/bin
activate      activate.fish  activate_this.py  easy_install   easy_install-3.5  pip3     pip3.5  python3    wheel   wheel-3.5
activate.csh  activate.ps1   activate.xsh      easy_install3  pip               pip-3.5  python  python3.5  wheel3

ubuntu@ip-172-31-47-18:~$ source django_udemy/bin/activate # 仮想環境をアクティベート
(django_udemy) ubuntu@ip-172-31-47-18:~$ pip install django gunicorn psycopg2 psycopg2-binary # 必要なライブラリをインストール
```

## プロジェクトをubuntu上に転送する

レクチャーには従わずgithub経由で行った

# マイグレーションとサーバーの動作確認

```
(django_udemy) ubuntu@ip-172-31-47-18:~/django_first$ pip install pillow
(django_udemy) ubuntu@ip-172-31-47-18:~/django_first/first_app/first_app$ vim settings.py # settingのDBの部分を書き換えた
```

ここで マイグレーションのコマンドが権限のせいで実行できない問題が発生した。UNIXではpeerという認証方式を使っているかららしい。

#### 参考記事
* https://techracho.bpsinc.jp/kazumasa-ogawa/2013_04_25/8244
* https://cpoint-lab.co.jp/article/201807/4217/

そこでdbの認証形式を書き換える

```
(django_udemy) ubuntu@ip-172-31-47-18:$ cd /etc/postgresql/9.5/main
(django_udemy) ubuntu@ip-172-31-47-18:/etc/postgresql/9.5/main$ ls -l
total 48
-rw-r--r-- 1 postgres postgres   315 May  5 12:25 environment
-rw-r--r-- 1 postgres postgres   143 May  5 12:25 pg_ctl.conf
-rwxrw-r-- 1 postgres postgres  4641 May  5 12:25 pg_hba.conf
-rw-r----- 1 postgres postgres  1636 May  5 12:25 pg_ident.conf
-rw-r--r-- 1 postgres postgres 21716 May  5 12:25 postgresql.conf
-rw-r--r-- 1 postgres postgres   378 May  5 12:25 start.conf
(django_udemy) ubuntu@ip-172-31-47-18:/etc/postgresql/9.5/main$ sudo chmod 766 pg_hba.conf
(django_udemy) ubuntu@ip-172-31-47-18:/etc/postgresql/9.5/main$ vim pg_hba.conf
(django_udemy) ubuntu@ip-172-31-47-18:/etc/postgresql/9.5/main$
```

`pg_hba.conf`の

```
local all postgres peer
```
の記述を
```
local all postgres md5
```
に書き換える。

```
sudo /etc/init.d/postgresql restart
```

これでDBを再起動する。

```
(django_udemy) ubuntu@ip-172-31-47-18:~$ python3 django_first/first_app/manage.py migrate
```

## 一旦8000番のポートを使えるようにする

セキュリティーグループのインバウンドルールを編集
ルールを追加
カスタムのTCP 8000 0.0.0.0/0 説明

```
(django_udemy) ubuntu@ip-172-31-47-18:~$ python3 django_first/first_app/manage.py runserver 0.0.0.0:8000
```

I made it!

バックエンドについてはgunivcornやnginxを導入していく

## Gunicornの動作確認

```
(django_udemy) ubuntu@ip-172-31-47-18:~/django_first/first_app$ gunicorn --bind 0.0.0.0:8000 first_app.wsgi # pathを.区切りで与える
# 動作を確認
(django_udemy) ubuntu@ip-172-31-47-18:~/django_first/first_app$ deactivate
```

## Gunicornの自動起動設定

```
ubuntu@ip-172-31-47-18:~/django_first/first_app/first_app$ sudo vim /etc/systemd/system/gunicorn.service # gunicornの設定を書き込む
ubuntu@ip-172-31-47-18:~/django_first/first_app/first_app$ sudo systemctl start gunicorn
ubuntu@ip-172-31-47-18:~/django_first/first_app/first_app$ sudo systemctl enable gunicorn
Created symlink from /etc/systemd/system/multi-user.target.wants/gunicorn.service to /etc/systemd/system/gunicorn.service
```

```/etc/systemd/system/gunicorn.service
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/django_first/first_app
ExecStart=/home/ubuntu/django_udemy/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/ubuntu/django_first/django_first.sock first_app.wsgi:application

[Install]
WantedBy=multi-user.target
```

もしもうまくいかないときは

```
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

でやり直して

```
sudo systemctl status gunicorn
```

で再びうまく動いているかを確認する

```
● gunicorn.service - gunicorn daemon
   Loaded: loaded (/etc/systemd/system/gunicorn.service; enabled; vendor preset: enabled)
   Active: active (running) since Wed 2020-05-06 04:20:18 UTC; 2min 57s ago
 Main PID: 2107 (gunicorn)
   CGroup: /system.slice/gunicorn.service
           ├─2107 /home/ubuntu/django_udemy/bin/python /home/ubuntu/django_udemy/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/ubuntu/django_first/django_first.sock fi
           ├─2112 /home/ubuntu/django_udemy/bin/python /home/ubuntu/django_udemy/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/ubuntu/django_first/django_first.sock fi
           ├─2113 /home/ubuntu/django_udemy/bin/python /home/ubuntu/django_udemy/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/ubuntu/django_first/django_first.sock fi
           └─2115 /home/ubuntu/django_udemy/bin/python /home/ubuntu/django_udemy/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/ubuntu/django_first/django_first.sock fi

May 06 04:20:18 ip-172-31-47-18 systemd[1]: Started gunicorn daemon.
May 06 04:20:18 ip-172-31-47-18 gunicorn[2107]: [2020-05-06 04:20:18 +0000] [2107] [INFO] Starting gunicorn 20.0.4
May 06 04:20:18 ip-172-31-47-18 gunicorn[2107]: [2020-05-06 04:20:18 +0000] [2107] [INFO] Listening at: unix:/home/ubuntu/django_first/django_first.sock (2107)
May 06 04:20:18 ip-172-31-47-18 gunicorn[2107]: [2020-05-06 04:20:18 +0000] [2107] [INFO] Using worker: sync
May 06 04:20:18 ip-172-31-47-18 gunicorn[2107]: [2020-05-06 04:20:18 +0000] [2112] [INFO] Booting worker with pid: 2112
May 06 04:20:18 ip-172-31-47-18 gunicorn[2107]: [2020-05-06 04:20:18 +0000] [2113] [INFO] Booting worker with pid: 2113
May 06 04:20:18 ip-172-31-47-18 gunicorn[2107]: [2020-05-06 04:20:18 +0000] [2115] [INFO] Booting worker with pid: 2115
```

こんな風になっていれば成功

### nginx

接続のイメージ
クライアント - nginx - gunicorn - django

```
ubuntu@ip-172-31-47-18:~/django_first/first_app$ cd /etc/nginx/
ubuntu@ip-172-31-47-18:/etc/nginx$ ls
conf.d  fastcgi.conf  fastcgi_params  koi-utf  koi-win  mime.types  nginx.conf  proxy_params  scgi_params  sites-available  sites-enabled  snippets  uwsgi_params  win-utf
ubuntu@ip-172-31-47-18:/etc/nginx$ cd sites-available/
ubuntu@ip-172-31-47-18:/etc/nginx/sites-available$ sudo vim firstapp
```

以下のように記述

```/etc/nginx/sites-available/firstapp
server {
        listen 80;
        server_name 13.114.88.188;

        location = /favicon.ico {access_log off; log_not_found off;}
        location /static/ {
                root /home/ubuntu/django_first/first_app;
        }

        location / {
                include proxy_params;
                proxy_pass http://unix:/home/ubuntu/django_first/django_first.sock;
        }
}
```

再びコマンド


```
ubuntu@ip-172-31-47-18:/etc/nginx/sites-available$ ls
default  firstapp
ubuntu@ip-172-31-47-18:/etc/nginx/sites-available$ sudo ln -s /etc/nginx/sites-available/firstapp /etc/nginx/sites-enabled/
ubuntu@ip-172-31-47-18:/etc/nginx/sites-available$ ls -la /etc/nginx/sites-enabled/
total 8
drwxr-xr-x 2 root root 4096 May  6 04:30 .
drwxr-xr-x 6 root root 4096 May  5 12:25 ..
lrwxrwxrwx 1 root root   34 May  5 12:25 default -> /etc/nginx/sites-available/default
lrwxrwxrwx 1 root root   35 May  6 04:30 firstapp -> /etc/nginx/sites-available/firstapp
ubuntu@ip-172-31-47-18:/etc/nginx/sites-available$ sudo nginx -t # テスト
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
ubuntu@ip-172-31-47-18:/etc/nginx/sites-available$ sudo systemctl restart nginx
ubuntu@ip-172-31-47-18:/etc/nginx/sites-available$ sudo ufw delete allow 8000 # ファイアーウォールの設定をいじる
Could not delete non-existent rule
Could not delete non-existent rule (v6)
ubuntu@ip-172-31-47-18:/etc/nginx/sites-available$ sudo ufw allow 'Nginx Full' # nginx を許可
Rules updated
Rules updated (v6)
ubuntu@ip-172-31-47-18:/etc/nginx/sites-available$ sudo systemctl restart gunicorn
```

これでnginxをつかってサイトを表示できる
