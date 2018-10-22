import re
from datetime import datetime, timedelta
from flask import jsonify, render_template, redirect, url_for, abort, flash, request, current_app, make_response
from flask_login import login_required, current_user
from flask_moment import Moment
from . import user
from .forms import PostForm
from .. import db
from ..models.ua_models import ua_user
from ..models.res_models import res_post, res_file, res_postclass

def filter_tags(htmlstr):
    dr = re.compile(r'<[^>]+>', re.S)
    dd = dr.sub('', htmlstr)

    return dd

def get_body_summary(body, strlen):

    return cutstr(filter_tags(body), strlen)

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

@user.route('/', methods=['GET'])
@user.route('/<int:classid>', methods=['GET'])
@login_required
def post_list(classid=None):
    
    return render_template('user/postlist.html', cid=classid)
    
@user.route('/classlist', methods=['GET'])
@user.route('/classlist/<int:classid>', methods=['GET'])
@login_required
def class_list(classid=None):
    
    return render_template('user/classlist.html', cid=classid)
    
@user.route('/moveclass/<int:classid>', methods=['GET'])
@user.route('/moveclass/<int:classid>/<string:type>/<int:id>', methods=['GET'])
@login_required
def move_view(classid, type=None, id=None):

    pagetitle =  "移动分类" if type == "class" else "移动笔记"
    cancelurl = url_for('user.post_list') if type == "post" else url_for('user.class_list')
    postclass = res_postclass.query.get(classid)
    levelupurl = url_for('user.move_view', classid=postclass.postclass_pid, type=type, id=id) if postclass else url_for('user.move_view', classid=0, type=type, id=id)
    
    return render_template('user/moveview.html', cid=classid, mvtype=type, optid=id, title=pagetitle, cancelurl=cancelurl, levelupurl=levelupurl)

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
            'nexturl': url_for('user.post_list')
        }
        
        return jsonify(result)
    
    return render_template('user/mdedit.html')

@user.route('/del/<int:postid>', methods=['GET'])
@login_required
def del_post(postid):

    post = res_post.query.get(postid)
    
    if current_user.user != post.author:
        abort(403)

    if post:

        db.session.delete(post)
        db.session.commit()

        result = {
            'code': 200,
            'msg': '笔记已删除',
            'nexturl': url_for('user.post_list')
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
    
        if 'classid' in request.form and request.form['classid'] != '':
            post.post_cid = request.form['classid']

        if 'name' in request.form and request.form['name'] != '':
            post.post_name = request.form['name']
            
        if 'body_md' in request.form and request.form['body_md'] != '':
            post.post_body_md = request.form['body_md']

        post.post_updatetime = datetime.utcnow()


        #data_query = db.session.execute("set names 'utf8mb4';")        
        db.session.add(post)
        db.session.commit()
        
        result = {
            'code': 200,
            'msg': '笔记已更新',
            'nexturl': url_for('user.post_list')
        }
        
        return jsonify(result)
    
    title = post.post_name
    content = post.post_body_md
    updatetime = post.post_updatetime.strftime("%Y/%m/%d %H:%M:%S")

    return render_template('user/mdedit.html', title=title, content=content, postid=postid, updatetime=updatetime)
    
@user.route('/postlistjson/<int:page>', methods=['GET'])
@user.route('/postlistjson/<int:page>/<int:cid>', methods=['GET'])
@login_required
def post_list_json(page, cid=None):

    if cid:
        pagination = res_post.query.filter_by(author_id=current_user.user.ua_user_id, post_cid=cid).order_by(res_post.post_updatetime.desc()).paginate(
            page, per_page=20, error_out=False)
    else:
        pagination = res_post.query.filter_by(author_id=current_user.user.ua_user_id).order_by(res_post.post_updatetime.desc()).paginate(
            page, per_page=20, error_out=False)
            
    posts = pagination.items

    result = {
        'hasnext': pagination.has_next,
        'posts': []
    }

    if pagination.has_next:
        if cid:
            result['nexturi'] = url_for('user.post_list_json', page=pagination.next_num, cid=cid)
        else:
            result['nexturi'] = url_for('user.post_list_json', page=pagination.next_num)

    for item in posts:
        post = {
            'id': item.post_id,
            'cid': item.post_cid if item.post_cid is not None else 0,
            'url': url_for('user.edit_post', postid=item.post_id),
            'title': cutstr(item.post_name, 35),
            'update': item.post_updatetime,
            'summary': get_body_summary(item.post_body_html, 150),
            'creat': item.post_createtime
        }

        result['posts'].append(post)

    return jsonify(result)
    
@user.route('/class/add', methods=['POST'])
@user.route('/class/<string:type>/add', methods=['POST'])
@login_required
def add_class(type=None):

    postclass = res_postclass(
        postclass_name=request.form['name'], 
        postclass_pid=request.form['pid'], 
        postclass_uid=current_user.user.ua_user_id)

    db.session.add(postclass)
    db.session.commit()
    
    nexturl = url_for('user.class_list', classid=postclass.postclass_pid) if postclass.postclass_pid else url_for('user.class_list')
    
    if type and type == 'mv':
        nexturl = url_for('user.move_view', classid=postclass.postclass_pid)
        
    result = {
        'code': 200,
        'msg': '分类已添加',
        'nexturl': nexturl
    }
    
    return jsonify(result)
    
    
@user.route('/class/del/<int:classid>', methods=['GET'])
@login_required
def del_class(classid):

    postclass = res_postclass.query.get(classid)
    
    if current_user.user != postclass.user:
        abort(403)

    if postclass:

        db.session.delete(postclass)
        db.session.commit()

        result = {
            'code': 200,
            'msg': '分类已删除',
            'nexturl': url_for('user.class_list', classid=postclass.postclass_pid) if postclass.postclass_pid else url_for('user.class_list')
        }
        
        return jsonify(result)

    result = {
        'code': 400,
        'msg': '删除失败'
    }
    
    return jsonify(result)
    
@user.route('/class/edit/<int:classid>', methods=['POST'])
@login_required
def edit_class(classid):

    postclass = res_postclass.query.get(classid)

    if current_user.user != postclass.user:
        abort(403)

    if postclass:
        if 'name' in request.form and request.form['name'] != '':
            postclass.postclass_name = request.form['name']
        
        if 'pid' in request.form and request.form['pid'] != '':
            postclass.postclass_pid = request.form['pid']

        db.session.add(postclass)
        db.session.commit()
        
        result = {
            'code': 200,
            'msg': '分类已更新',
            'nexturl': url_for('user.class_list', classid=postclass.postclass_pid) if postclass.postclass_pid else url_for('user.class_list')
        }
        
        return jsonify(result)
        
        
@user.route('/class/classlistjson/<int:page>', methods=['GET'])
@user.route('/class/classlistjson/<int:page>/<int:pid>', methods=['GET'])
@login_required
def class_list_json(page, pid=None):

    if pid == None:
        pid = 0
        
            
    pagination = res_postclass.query.filter_by(postclass_uid=current_user.user.ua_user_id, postclass_pid=pid).order_by(
            res_postclass.postclass_createtime.desc()).paginate(page, per_page=20, error_out=False)
            
    classes = pagination.items

    result = {
        'hasnext': pagination.has_next,
        'classes': []
    }

    if pagination.has_next:
        result['nexturi'] = url_for('user.class_list_json', page=pagination.next_num),

    
    for item in classes:
        class_item = {
            'id': item.postclass_id,
            'name': cutstr(item.postclass_name, 35),
            'post_url': url_for('user.post_list', classid=item.postclass_id),
            'class_url': url_for('user.class_list', classid=item.postclass_id),
            'move_url': url_for('user.move_view', classid=item.postclass_id),
            'post_count': item.postcount,
            'creat': item.postclass_createtime
        }

        result['classes'].append(class_item)

    return jsonify(result)
    

@user.route('/uploadfile/<file_name>/<path:type_name>', methods=['POST'])
def upload_img(file_name, type_name):

    filemodel = res_file(file_name=file_name, file_type=type_name, file_data=request.data, file_uid=current_user.user.ua_user_id)
    db.session.add(filemodel)
    db.session.commit()

    result = {
        'code': 200,
        'name': filemodel.file_name,
        #'url': current_app.config['WEB_HOST'] + url_for('user.file_get', fileid=image.file_id)
        'url': url_for('user.file_get', fileid=filemodel.file_id)
    }

    return jsonify(result)

@user.route('/file/<int:fileid>', methods=['GET'])
def file_get(fileid):

    file = res_file.query.get(fileid)
    
    response = make_response(file.file_data)
    response.mimetype = file.file_type

    return response

