from flask import Flask, render_template, url_for, request, redirect, json, flash
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import func

from sweater import app, db
from sweater.models import User, Article, Tag, Comment


@app.route('/', methods=['GET','POST'])
def index():
    """ Возвращает главную страницу через GET
    POST метод для реализации Search """
    if request.method == 'GET':
        sender = User.query.filter_by(login='Sendnuds').first()
        articles = Article.query.outerjoin(Comment).group_by(Article.id).order_by(func.count(Comment.id).desc()).all()[:3]
        sends = Article.query.filter_by(owner=sender).all()
        return render_template('index.html', articles = articles, sends=sends)
    else:
        q = request.form['text']
        if q:
            articles = Article.query.filter(Article.title.contains(q) | Article.text.contains(q))
            result = []
            for art in articles:
                result.append({'id':art.id, 'title':art.title, 'cut':art.cut})
            return json.dumps(result)
        else: 
            return json.dumps('')
        # return render_template('index.html', 


@app.route('/article', methods=['GET','POST'])
@login_required
def new_article():
    if request.method == 'GET':
        return render_template('new_state.html', article=None)
    else:
        try:
            title = request.form['title']
            text = request.form['text']
            tags = json.loads(request.form['tags'])
            tgs = []
            # Парсим тэги
            for tag in tags:
                if Tag.query.filter_by(name=tag).first() is None:
                    tg = Tag(name=tag)
                    db.session.add(tg)
                    tgs.append(tg)
                else:
                    tg = Tag.query.filter_by(name=tag).first()
                    tgs.append(tg)
            # Создаем запись в БД
            cut = text[:64]+'...'
            art = Article(title=title, cut=cut, text=text, owner=current_user, tags=tgs)
            db.session.add(art)
            db.session.commit()
            print("art id is ", art.id)
            return json.dumps({
                'artId':art.id,
                'status':'success',
            })
        except Exception as e:
            print("Exception is ", e)
            return json.dumps({
                'status':'fail',
                'msg':e
            })


@app.route('/article/<art>', methods=['GET', 'POST'])
def article(art):
    article = Article.query.filter_by(id=int(art)).first()
    if request.method == 'POST': # Add comment code
        comment = Comment(text=request.form['text'], owner=current_user, article=article)
        db.session.add(comment)
        db.session.commit()
        return json.dumps({
            'id': comment.id,
            'owner':comment.owner.login,
            'text':comment.text,
            'date':comment.date})
    else: # Just show page 
        return render_template('article.html', article=article)


@app.route('/article/change/<art>', methods=['GET', 'POST'])
def change_article(art):
    article = Article.query.filter_by(id=int(art)).first()
    if request.method == 'POST':
        try:
            title = request.form['title']
            text = request.form['text']
            tags = json.loads(request.form['tags'])
            tgs = []
            # Парсим тэги
            for tag in tags:
                if Tag.query.filter_by(name=tag).first() is None:
                    tg = Tag(name=tag)
                    db.session.add(tg)
                    tgs.append(tg)
                else:
                    tg = Tag.query.filter_by(name=tag).first()
                    tgs.append(tg)
            # Создаем запись в БД
            article.title = title
            article.text = text
            article.tags = tgs
            db.session.add(article)
            db.session.commit()
            return json.dumps({
                'artId': article.id,
                'status':'success',
            })
        except Exception as e:
            print("Exception is ", e)
            return json.dumps({
                'status':'fail',
                'msg':e
            })
    else:
        return render_template('new_state.html', article=article)


# Удаление статьи 
@app.route('/article/delete/<art>')
def del_art(art):
    article = Article.query.filter_by(id=int(art)).first()
    db.session.delete(article)
    for comment in article.comments:
        db.session.delete(comment)
    db.session.commit()
    return redirect('/')


# Удаление комментария 
@app.route('/comment/delete', methods=['POST',])
def del_comm():
    try:
        comment = Comment.query.filter_by(id=int(request.form['comment'])).first()
        db.session.delete(comment)
        db.session.commit()
        return json.dumps({'status':'success'})
    except:
        return json.dumps({'status':'error'})


@app.route('/comment/change', methods=['POST',])
def change_comm():
    comment = Comment.query.filter_by(id=int(request.form['id'])).first()
    comment.text = request.form['text']
    db.session.add(comment)
    db.session.commit()
    return json.dumps({'status':'success'})
    


@app.route('/blog')
def blog():
    page = request.args.get('page')
    q = request.args.get('q')
    # Пагинация 
    if page and page.isdigit():
        page = int(page)
    else: 
        page = 1
    # Запрос поиска
    if q:
        articles = Article.query.filter(Article.title.contains(q) | Article.text.contains(q))
    else:
        articles = Article.query

    pages = articles.paginate(page=page, per_page=3)

    return render_template('blog.html', articles=articles, pages=pages, q=q)

@app.route('/blog/<username>')
def user_blog(username):
    owner = User.query.filter_by(login=username).first()
    # Вставить обработчик 404
    page = request.args.get('page')
    q = request.args.get('q')

    if page and page.isdigit():
        page = int(page)
    else: 
        page = 1

    if q:
        articles = Article.query.filter(Article.title.contains(q) | Article.text.contains(q)).filter_by(owner=owner)
    else:
        articles = Article.query.filter_by(owner=owner) 

    pages = articles.paginate(page=page, per_page=3)

    count = Article.query.filter_by(owner=owner).count()
    

    return render_template('blog_user.html', owner=owner, articles=articles, pages=pages, q=q, count=count)


     

# LOGIN MANAGMENT 

@app.route('/registration', methods=['GET','POST'])
def registration():
    if request.method == 'GET':
        return render_template('registration.html')
    else:
        try: 
            login = request.form['login'].title()
            if User.query.filter_by(login=login).first() is not None:
                return json.dumps({
                    'status':'fall',
                    'message':'The login is busy'
                })
            # email = request.form['email']
            # if User.query.filter_by(email=email).first() is not None:
            #     return json.dumps({
            #         'status':'fall',
            #         'message':'The email is busy'
            #     })
            if request.form['password'] != request.form['password_confirm']:
                return json.dumps({
                    'status':'fall',
                    'message':'Pass1 must be == Pass2'
                })
            # If success
            user = User(login=login,email='%s@test.com'%login,password=request.form['password'])
            db.session.add(user)
            db.session.commit()
            return json.dumps({
                'status':'success',
                'message':'Аккаунт успешно создан!'
            })
        except Exception as e:
            print("Error is ", e)
            return json.dumps({
                'status':'fail',
                'message':'Неизвестная ошибка сервера. Попробуйте снова'
            })


@app.route('/check_login', methods=['POST'])
def check_login():
    if User.query.filter_by(login=request.form['login'].title()).first() is not None:
        return json.dumps('fail')
    else: 
        return json.dumps('success')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=="POST":
        login = request.form['login'].title()
        password = request.form['password']
        try:
            user = User.query.filter_by(login=login).first()
            if user is None:
                return json.dumps({
                    'status': 'fail',
                    'message': 'Login is not registration'
                })
            if user.password == password:
                login_user(user)
                return json.dumps({
                    'status': 'success',
                    'message': 'Welcome in'
                })
            else: 
                return json.dumps({
                    'status': 'fail',
                    'message': 'Password inccorect'
                })
        except Exception:
            return json.dumps({
                'status': 'fail',
                'message': 'Database error'
            })
    else:
        return render_template('login.html')


@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')

