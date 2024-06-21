import shutil
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, send_file, current_app
from flask_login import login_required, current_user
import os
import zipfile
from threading import Thread
from .tasks import threaded_task
from .models import Execution
from .source import fuso_horario
from .log import LOG

from app import db

main = Blueprint('main', __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@main.route('/')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template('login.html')


@main.route('/index')
@login_required
def index():
    return render_template('index.html', usuario=current_user)


@main.route('/config')
@login_required
def config():
    if not current_user.admin:
        return redirect(url_for('main.index'))
    return render_template('config.html', usuario=current_user)


@main.route('/execs')
@login_required
def execs():
    all_execs = Execution.query.order_by(Execution.id.desc()).all()
    return render_template('execs.html', usuario=current_user, executions=all_execs)


def get_folders():
    folders = []
    for x in os.listdir('app/images'):
        if os.path.isdir('app/images/' + x):
            folders.append(x)
    return folders


@main.route('/new_exec')
@login_required
def new_exec_get():
    folders = get_folders()
    return render_template('new_exec.html', usuario=current_user, folders=folders)


@main.route('/new_exec', methods=['POST'])
@login_required
def new_exec():
    folder = request.form.get('folder')
    iqa_exec = Execution(folder=folder,
                            date=datetime.now().astimezone(fuso_horario),
                            progress=50,
                            result_filename=''
                            )
    db.session.add(iqa_exec)
    db.session.commit()
    print(iqa_exec, iqa_exec.progress)
    LOG(f'\nA\n')
    thread = Thread(target=threaded_task, args=(current_app.app_context(), folder, iqa_exec, db))
    thread.daemon = True
    thread.start()
    LOG(f'\nB\n')
    return redirect(url_for('main.execs'))

    return redirect(url_for('main.new_exec_get'))


@main.route('/delete_exec/<exec_id>')
@login_required
def delete_exec(exec_id):
    execution = Execution.query.get(exec_id)
    if current_user.admin or (execution.progress == 100):
        db.session.delete(execution)
        try:
            if execution.result_filename != '':
                os.remove('app/results/' + execution.result_filename)
        except Exception as e:
            print(e)
        db.session.commit()
    return redirect(url_for('main.execs'))


@main.route('/upload', methods=['POST'])
@login_required
def upload():
    file = request.files.get('file')
    if file and (file.filename.split('.')[-1] == 'h5' or file.filename.split('.')[-1] == 'tf'):
        file.save('app/model.h5')
    return redirect(url_for('main.config'))


@main.route('/download/<path:filename>', methods=['GET'])
@login_required
def download_file(filename):
    path = "results/" + filename
    return send_file(path, as_attachment=True)


def unzip_file(zip_src, dst_dir):
    r = zipfile.is_zipfile(zip_src)
    if r:
        fz = zipfile.ZipFile(zip_src, "r")
        for file in fz.namelist():
            fz.extract(file, dst_dir)
    else:
        return "Please upload a compressed file of zip type"


def get_used_disk_space():
    t, u, f = shutil.disk_usage("/")
    used = int((u / t) * 100)
    total = t // (2**30)
    return used, total


@main.route("/upload_images", methods=["GET", "POST"])
def upload_images():
    if request.method == "GET":
        folders = get_folders()
        used, total = get_used_disk_space()
        return render_template("upload_images.html", usuario=current_user, folders=folders, used=used, total=total)
    obj = request.files.get("file")
    ret_list = obj.filename.rsplit(".", maxsplit=1)
    if len(ret_list) != 2:
        return "Please upload a compressed file of zip type"
    if ret_list[1] != "zip":
        return "Please upload a compressed file of zip type"

    file_path = os.path.join(BASE_DIR, "images", obj.filename)
    obj.save(file_path)
    target_path = os.path.join(BASE_DIR, "images")
    ret = unzip_file(file_path, target_path)
    os.remove(file_path)
    return redirect(url_for('main.upload_images'))


@main.route('/delete_folder/<folder>')
@login_required
def delete_folder(folder):
    if current_user.admin:
        shutil.rmtree('app/images/' + folder)
    return redirect(url_for('main.upload_images'))

