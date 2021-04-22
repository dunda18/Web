from flask import Flask, url_for, request, render_template, redirect

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from werkzeug.security import generate_password_hash, check_password_hash

from data import db_session
from data.chats import Chat
from data.messages import Message
from data.users import User
from data.users_chats import User_Chat

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
    # do_register = SubmitField('Регистрация')


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    login = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Зарегистрироваться')


class CreateChatForm(FlaskForm):
    title = StringField('Название чата', validators=[DataRequired()])
    submit = SubmitField('Создать')


class ChatForm(FlaskForm):
    message = StringField('Cообщение', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class AddUserToChat(FlaskForm):
    login = StringField('Имя пользователя', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class EditProfile(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Сохранить')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # if form.do_register.data:
    #     return redirect('/register')

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)

    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.login == form.login.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким логином уже есть")
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким email уже есть")
        user = User(
            login=form.login.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        cur_user_id = current_user.id
        chats = db_sess.query(Chat).filter(Chat.id.in_([i.chat_id for i in db_sess.query(User_Chat).
                                           filter(User_Chat.user_id == cur_user_id).all()])).all()
    else:
        chats = []
    return render_template("index.html", title='Личный кабинет', chats=chats)


@app.route('/create_chat', methods=['GET', 'POST'])
@login_required
def create_chat():
    form = CreateChatForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        chat = Chat()
        chat.title = form.title.data
        db_sess.add(chat)

        chat = db_sess.query(Chat).filter(Chat.title == chat.title).first()

        user_chat = User_Chat()
        user_chat.user_id = current_user.id
        user_chat.chat_id = chat.id

        db_sess.add(user_chat)
        db_sess.commit()
        return redirect('/')
    return render_template("create_chat.html", title='Создание чата', form=form)


@app.route('/chats/<int:id>', methods=['GET', 'POST'])
@login_required
def chat(id):
    db_sess = db_session.create_session()

    form = ChatForm()
    chat = db_sess.query(Chat).filter(Chat.id == id).first()

    if not chat:
        return render_template("chat_not_found.html", title='Чат не найден')

    user = db_sess.query(User).filter(User.id == current_user.id).first()

    if not db_sess.query(User_Chat).filter((User_Chat.user_id == user.id) & (User_Chat.chat_id == chat.id)).first():
        return render_template("kuda_polez.html", title='Чат')

    if form.validate_on_submit():
        message = Message()
        message.text = form.message.data

        message.user = user
        message.chat = chat
        # chat.messages.append(message)
        # current_user.messages.append(message)
        db_sess.add(message)
        db_sess.commit()
        form.message.data = ''

    return render_template("chat.html", title='Чат', form=form, chat_title=chat.title, chat=chat)


@app.route('/add_user_to_chat/<int:id>', methods=['GET', 'POST'])
@login_required
def add_user_to_chat(id):
    db_sess = db_session.create_session()

    form = AddUserToChat()
    chat = db_sess.query(Chat).filter(Chat.id == id).first()
    user = db_sess.query(User).filter(User.id == current_user.id).first()

    if form.validate_on_submit():
        new_user = db_sess.query(User).filter(User.login == form.login.data).first()

        if new_user:
            if db_sess.query(User_Chat).filter((User_Chat.user_id == new_user.id) &
                                               (User_Chat.chat_id == chat.id)).first():
                return render_template("add_user_to_chat.html", title='Добавление в чат',
                                       form=form, message="Пользователь уже состоит в этом чате")

            user_chat = User_Chat()
            user_chat.user_id = new_user.id
            user_chat.chat_id = chat.id
            db_sess.add(user_chat)
            db_sess.commit()

            return render_template("add_user_to_chat.html", title='Добавление в чат',
                                   form=form, message="Пользователь успешно добавлен")
        else:
            return render_template("add_user_to_chat.html", title='Добавление в чат', form=form,
                                   message="Пользователь не найден")

    return render_template("add_user_to_chat.html", title='Добавление в чат', form=form)


@app.route('/profile/<int:id>', methods=['GET', 'POST'])
def profile(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    if not user:
        return render_template("profile_error.html", title='Профиль')

    return render_template("profile.html", title='Профиль', user=user)


@app.route('/profile_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def profile_edit(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    if not user:
        return render_template("profile_error.html", title='Редактировать профиль')

    if user.id != current_user.id:
        return render_template("profile_edit_error.html", title='Редактировать профиль')

    form = EditProfile()
    if form.validate_on_submit():
        user.email = form.email.data
        user.about = form.about.data
        db_sess.commit()
        return redirect('/profile/' + str(id))

    form.email.data = user.email
    form.about.data = user.about
    return render_template("profile_edit.html", title='Редактировать профиль', form=form)


if __name__ == '__main__':
    db_session.global_init("db/chat.db")
    app.run(port=8080, host='127.0.0.1')