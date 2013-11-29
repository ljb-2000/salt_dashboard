#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/11/14 14:42
from flask import Flask, url_for, redirect, render_template, request, flash, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from wtforms import form, fields, validators
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext import admin, login
from flask.ext.admin.contrib import sqla
from flask.ext.admin.actions import action
from flask.ext.admin import helpers, expose, BaseView
from flask.ext.babelex import Babel


# Create application
app = Flask(__name__)
babel = Babel(app)


@babel.localeselector
def get_locale():
    # Put your logic here. Application can store locale in
    # user profile, cookie, session, etc.
    return 'zh'

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = 'qOH7fBkvial$%P^kWq3#J30gqMiV0rbQ'

# Create mysql  database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://salt:D215&ARm!cm63wf%@172.16.10.85:3306/salt'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

# Create user model. For simplicity, it will store passwords in plain text.
# Obviously that's not right thing to do in real world application.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(66))

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username


class IDC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text())
    country = db.Column(db.String(64))
    province = db.Column(db.String(64))
    city = db.Column(db.String(64))

    def __unicode__(self):
        return self.name


class Host(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text())
    public_ip = db.Column(db.String(64))
    public_ip_secondary = db.Column(db.String(64))
    private_ip = db.Column(db.String(64))
    group_id = db.Column(db.Integer, db.ForeignKey('host_group.id'))
    saltversion = db.Column(db.String(64), default='0')
    grains = db.Column(db.String(128))
    group = db.relationship('HostGroup', backref='groups')


    def __unicode__(self):
        return self.name


class HostGroup(db.Model):
    __tablename__ = 'host_group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text())


    def __unicode__(self):
        return self.name


class LoginForm(form.Form):
    login = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')
            #if user.password != generate_password_hash(self.password.data):
        if not check_password_hash(user.password, self.password.data):
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(User).filter_by(login=self.login.data).first()


class RegistrationForm(form.Form):
    login = fields.TextField(validators=[validators.required()])
    email = fields.TextField()
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        if db.session.query(User).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('Duplicate username')


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)


# Create customized model view class
class UserModelView(sqla.ModelView):
    column_searchable_list = ('login', User.login)
    column_filters = ('login', User.login)
    column_exclude_list = ('password')
    column_labels = dict(login=u'登录名', email=u'邮件地址', password=u'密码')

    def is_accessible(self):
        return login.current_user.is_authenticated()

    def on_model_change(self, form, model, is_created=True):
        if form.data.has_key('password'):
            model.password = generate_password_hash(form.data['password'])
            #form.data['password'] = generate_password_hash(form.data['password'])


class HostModelView(sqla.ModelView):
    column_labels = dict(
        group=u'群组', name=u'主机名', description=u'描述', public_ip=u'公网地址(电信)',
        public_ip_secondary=u'公网地址(联通)', private_ip=u'私网地址', saltversion=u'salt版本')

    @action(name='json', text=u'导出为json', confirmation=None)
    def print_host(self, ids):
        '''
        print "*" * 60
        from flask.ext.admin.contrib.sqla.tools import is_inherited_primary_key, get_column_for_current_model, get_query_for_ids

        query = get_query_for_ids(self.get_query(), self.model, ids)
        aaa = {}
        for host in query.all():
            print "*" * 60
            #aaa = dict((col, getattr(host, col)) for col in host.__table__.columns.keys())
            print dir(host)
            print "*" * 60
        '''
        return redirect(url_for('salt.test', foo='123'))

    def is_accessible(self):
        return login.current_user.is_authenticated()


class IDCModelView(sqla.ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated()


class HostGroupModelView(sqla.ModelView):
    column_labels = dict(
        name=u'群组名', description=u'描述', groups=u'组成员')

    def is_accessible(self):
        return login.current_user.is_authenticated()

# Create customized index view class


class MyAdminIndexView(admin.AdminIndexView):
    @expose('/')
    def home(self):
        return self.render('home.html')

    def is_accessible(self):
        return login.current_user.is_authenticated()


class SaltIndexView(BaseView):
    @expose('/')
    def index(self):
        form = RegistrationForm(request.form)
        return self.render('test.html', form=form)

    @expose('/test/')
    def test(self):
        return self.render('test.html')

    def is_accessible(self):
        return login.current_user.is_authenticated()

# Flask views
@app.route('/')
def index():
    return render_template('index.html', user=login.current_user)


@app.route('/login/', methods=('GET', 'POST'))
def login_view():
    form = LoginForm(request.form)
    if helpers.validate_form_on_submit(form):
        user = form.get_user()
        login.login_user(user)
        return redirect(url_for('index'))

    return render_template('form.html', form=form)


@app.route('/register/', methods=('GET', 'POST'))
def register_view():
    form = RegistrationForm(request.form)
    if helpers.validate_form_on_submit(form):
        user = User()
        form.password.data = unicode(generate_password_hash(form.password.data))
        form.populate_obj(user)
        db.session.add(user)
        db.session.commit()

        login.login_user(user)
        return redirect(url_for('index'))

    return render_template('form.html', form=form)


@app.route('/logout/')
def logout_view():
    login.logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Initialize flask-login
    init_login()

    # Create admin
    admin = admin.Admin(app, 'Salt Admin', index_view=MyAdminIndexView())

    # Add view
    admin.add_view(UserModelView(User, db.session, name=u'用户管理'))
    admin.add_view(HostModelView(Host, db.session, name=u'主机', category=u'主机管理'))
    admin.add_view(HostGroupModelView(HostGroup, db.session, name=u'群组', category=u'主机管理'))
    admin.add_view(SaltIndexView(name="Salt", endpoint='salt'))
    #admin.add_view(IDCModelView(IDC, db.session))

    # Create DB
    db.create_all()

    # Start app
    app.run(debug=True)