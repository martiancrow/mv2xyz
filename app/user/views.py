import re
from datetime import datetime, timedelta
from flask import jsonify, render_template, redirect, url_for, abort, flash, request, current_app, make_response
from flask_login import login_required, current_user
from flask_moment import Moment
from . import user
from .forms import PostForm
from .. import db
from ..models.ua_models import ua_user
from ..models.res_models import res_post, res_file

def filter_tags(htmlstr):
    dr = re.compile(r'<[^>]+>', re.S)
    dd = dr.sub('', htmlstr)

    return dd

def get_body_summary(body, strlen):

    return cutstr(filter_tags(body), 100)

def cutstr(src, strlen):

    if src:
        if len(src) > strlen:

            src = src[:strlen]

            if len(src) != 0:
                src += '...'

    return src

@user.before_app_request
def before_request():
    current_user

@user.route('/', methods=['GET', 'POST'])
@login_required
def index():
    
    return render_template('user/index.html')

@user.route('/postlistjson/<int:page>', methods=['GET'])
@login_required
def post_list_json(page):

    pagination = res_post.query.order_by(res_post.post_updatetime.desc()).paginate(
        page, per_page=20, error_out=False)
    posts = pagination.items

    result = {
        'hasnext': pagination.has_next,
        'posts': []
    }

    if pagination.has_next:
        result['nexturi'] = url_for('user.post_list_json', page=pagination.next_num),

    for item in posts:
        post = {
            'url': url_for('user.edit_post', postid=item.post_id),
            'title': cutstr(item.post_name, 35),
            'update': item.post_updatetime,
            'summary': get_body_summary(item.post_body_html, 100),
            'creat': item.post_creattime
        }

        result['posts'].append(post)

    return jsonify(result)

@user.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():

    return render_template('user/profile.html', user=current_user.user)

@user.route('/add', methods=['GET', 'POST'])
@login_required
def add_post():

    if request.method == 'POST':

        post = res_post(
            post_name=request.form['name'], 
            post_body_md=request.form['body_md'], 
            author_id=current_user.user.ua_user_id)


        db.session.add(post)
        db.session.commit()

        result = {
            'code': 200,
            'msg': '笔记已添加',
            'nexturl': url_for('user.index')
        }
        
        return jsonify(result)
    
    return render_template('user/mdedit.html')

@user.route('/del/<int:postid>', methods=['GET'])
@login_required
def del_post(postid):

    post = res_post.query.get(postid)

    if post:

        db.session.delete(post)
        db.session.commit()

        result = {
            'code': 200,
            'msg': '笔记已删除',
            'nexturl': url_for('user.index')
        }
        
        return jsonify(result)

    result = {
        'code': 400,
        'msg': '删除失败'
    }
    
    return jsonify(result)

@user.route('/edit/<int:postid>', methods=['GET', 'POST'])
@login_required
def edit_post(postid):

    post = res_post.query.get_or_404(postid)

    if current_user.user != post.author:
        abort(403)

    if request.method == 'POST':

        print(request.form['body_md'])

        post.post_name = request.form['name']
        post.post_body_md = request.form['body_md']
        post.post_updatetime = datetime.utcnow()



        db.session.add(post)
        db.session.commit()
        
        result = {
            'code': 200,
            'msg': '笔记已更新',
            'nexturl': url_for('user.index')
        }
        
        return jsonify(result)
    
    title = post.post_name
    content = post.post_body_md
    updatetime = post.post_updatetime.strftime("%Y/%m/%d %H:%M:%S")

    return render_template('user/mdedit.html', title=title, content=content, postid=postid, updatetime=updatetime)

@user.route('/uploadimg/<file_name>/<path:type_name>', methods=['POST'])
def upload_img(file_name, type_name):

    image = res_file(file_name=file_name, file_type=type_name, file_data=request.data)
    db.session.add(image)
    db.session.commit()

    result = {
        'code': 200,
        'name': image.file_name,
        #'url': current_app.config['WEB_HOST'] + url_for('user.file_get', fileid=image.file_id)
        'url': url_for('user.file_get', fileid=image.file_id)
    }

    return jsonify(result)

@user.route('/file/<int:fileid>', methods=['GET'])
def file_get(fileid):

    file = res_file.query.get(fileid)
    
    response = make_response(file.file_data)
    response.mimetype = file.file_type

    return response

