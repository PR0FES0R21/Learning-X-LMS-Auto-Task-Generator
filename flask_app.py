from flask import Flask, request, render_template, jsonify, Response, redirect, url_for, send_file, session
import pymongo
from pymongo import MongoClient
import os
from io import StringIO
import html
import shutil
import jwt
import datetime
import uuid

from os.path import dirname, join
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DB_HOST = os.environ.get("MONGODB_URL")
DB_NAME = os.environ.get("DB_NAME")

client = MongoClient(DB_HOST)
db = client[DB_NAME]

app = Flask(__name__)
app.secret_key = 'profesor'

@app.route('/')
def index():
    updateSession()
    session['email'] = None
    if 'login' in session and session['login']:
        return render_template('index.html')
    else:
        return redirect(url_for('view_login'))


#########################################################################
#                        fitur untuk menambahkan User                   #
#########################################################################
@app.route('/add/user')
def tambahUser():
    if 'login' not in session or (session['login'] and session.get('level') != 'Administrator'):
        return redirect(url_for('index'))
    
    msg = request.args.get('msg')
    type = request.args.get('type')
    return render_template('tambah_user.html', msg=msg, type=type)

@app.route('/add/user', methods=['POST'])
def addUser():
    username = html.escape(request.form.get('username'))
    password = html.escape(request.form.get('password'))
    name = html.escape(request.form.get('name'))
    mongodb_url = request.form.get('mongodb-url')
    dbname = html.escape(request.form.get('dbname'))
    email = html.escape(request.form.get('email'))
    name = html.escape(request.form.get('name'))
    level = html.escape(request.form.get('level'))
    
    last_user = db.users.find_one(sort=[("id", pymongo.DESCENDING)])
    if last_user:
        last_id = int(last_user["id"])
    else:
        last_id = 0
        
    new_id = last_id + 1
    
    doc = {
        'name': name,
        'username': username,
        'password': password,
        'mongodbUrl': mongodb_url,
        'dbname': dbname,
        'name': name,
        'email': email,
        'level': level,
        'id': new_id,
        'selesai': 0,
        'profile': 'default_image.jpg',
        'register_date': datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    }

    result = db.users.insert_one(doc)
    if(result.acknowledged):
        msg = 'Data Berhasil Ditambahkan.'
        type = 'success'
    else:
        msg = 'Data Gagal Ditambahkan.'
        type = 'danger'
    return redirect(url_for('tambahUser', msg=msg, type=type))
######################### END FITUR ADD USER ##########################


@app.route('/directory')
def directory():
    if 'login' not in session or (session['login'] and session.get('level') != 'Administrator'):
        return redirect(url_for('index'))
    
    base_path = 'file'
    file_path = 'final_file'
    
    folder_names = [folder for folder in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, folder))]

    file_list = [file for file in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, file))]
    
    return render_template('directory.html', folder_names=folder_names, file_list=file_list)


#########################################################################
#                   fitur untuk menambahkan folder atau tugas           #
#########################################################################
@app.route('/add/file')
def add_file():
    if 'login' not in session or (session['login'] and session.get('level') != 'Administrator'):
        return redirect(url_for('index'))
    return render_template('add_tugas.html')


@app.route('/save_file', methods=['POST'])
def save_file():
    file = request.files['file-tugas']
    tugasName = request.form.get('nama-tugas')
    keterangan = request.form.get('keterangan')

    filename = file.filename

    file.save(f'zipfile/{filename}')

    db.file_tugas.insert_one({
        'fileName': filename.split(".")[0],
        'tugasName': tugasName,
        'keterangan': keterangan
    })

    ekstrak_file(filename)

    return redirect(url_for('add_kuis', data=filename.split(".")[0]))
########################## END FITUR ######################

#########################################################################
#                   fitur untuk mengerjakan tugas                       #
#########################################################################
@app.route('/kerjakan/tugas')
def kerjakan_tugas():
    
    if 'login' in session and session['login']:
        username = request.args.get('username')
        filename = request.args.get('filename')
        status = request.args.get('status')
        
        return render_template('page_tugas.html', filename=filename, username=username, status=status)
    else:
        return redirect(url_for('view_login'))
############################### END FITUR ################################


@app.route('/add/kuis')
def add_kuis():
    if 'login' not in session or (session['login'] and session.get('level') != 'Administrator'):
        return redirect(url_for('index'))
    data = request.args.get('data')
    return render_template('add_kuis.html', data=data)

@app.route('/add/kuis', methods=['POST'])
def addKuis():
    nomorKuis = request.form.get('nomor-kuis')
    soalKuis = request.form.get('soal-kuis')
    jawabanKuis = request.form.get('jawaban-kuis')
    
    db.kuis.insert_one({
        'nomorKuis': nomorKuis,
        'soalKuis': soalKuis,
        'jawabanKuis': jawabanKuis
    })
    return redirect(url_for('add_kuis', data=nomorKuis))


@app.route('/confirmasi/tugas')
def confirmasiTugas():
    return render_template('confirmasi_tugas.html')

@app.route('/delete/data', methods=['POST'])
def deleteData():
    collection_name = request.form.get('collection')
    key = request.form.get('key')
    value = request.form.get('value')
    
    collection = db[collection_name]
    result = collection.delete_many({key: value})

    if result.acknowledged:
        return jsonify({'msg': 'Semua Data Berhasil Dihapus'})
    else:
        return jsonify({'msg': 'Data Gagal Dihapus'})

    
@app.route('/confirmasi/tugas', methods=['POST'])
def confirmasi_tugas():
    minggu = request.form.get('minggu')
    user = request.form.get('user')
    user_agent = request.form.get('user_agent')
    
    # Periksa apakah 'user_name' ada dalam sesi
    if user == 'false':
        user = session.get('user_name')

    # Mendapatkan tanggal dan waktu saat ini

    now = datetime.datetime.now()
    date = now.strftime('%d-%b-%y')
    time = now.strftime('%H.%M.%S')
    
    jumlah_document = db.confirm.count_documents({'name': user})
    db.users.update_one({'username': user}, {'$set': {'selesai': jumlah_document + 1}})

    doc = {
        'name': str(user),
        'minggu': minggu,
        'date': str(date),
        'time': str(time),
    }
    
    db.confirm.insert_one(doc)
    doc = ({
        'ip': request.remote_addr,
        'user_agent': user_agent,
        'device': request.user_agent.platform,
        'browser': request.user_agent.browser,
        'version': request.user_agent.version,
        'id': session['id'],
        'actifity': f'konfirmasi minggu {minggu}',
        'waktu': datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    })
    db.tracking.insert_one(doc)
    return jsonify({'name': user})

@app.route('/get/confirmasi/tugas', methods=['GET'])
def getConfirmasiTugas():
    user = request.args.get('name')
    data = getdataBykey('confirm', 'name', user)
    return data


@app.route('/kelola/user')
def kelolaUser():
    msg = request.args.get('msg')
    return render_template('kelola_user.html', msg=msg)

@app.route('/detail/user', methods=['GET'])
def detailUser():
    name = request.args.get('name')
    return render_template('detail_user.html', name=name)

@app.route('/update/user', methods=['GET'])
def updateUser():
    username = request.args.get('username')
    data = getdataByName(username)
    return data

@app.route('/update/user', methods=['POST'])
def update_user():
    
    name = request.form.get('name')
    username = request.form.get('username')
    password = request.form.get('password')
    mongodburl = request.form.get('mongodb-url')
    dbname = request.form.get('dbname')
    email = request.form.get('email')
    level = request.form.get('level')
    
    user_old = db.users.find_one({'username': username}, {'_id': False})
    user_old['update_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H.%M.%S')
    db.update_user.insert_one(user_old)
    
    doc_filter = {'username': username}

    doc_update = {
        '$set': {
            'name': name,
            'username': username,
            'password': password,
            'mongodbUrl': mongodburl,
            'dbname': dbname,
            'email': email,
            'level': level
        }
    }
    
    db.users.update_one(doc_filter, doc_update)
    return redirect(url_for('kelolaUser', msg=f'Data {username} Berhasil Diperbarui'))

@app.route('/check', methods=['GET'])
def checkUsername():
    query = request.args.get('q')
    result = db.users.find_one({'username': query})
    return jsonify({'exists': result is not None})

@app.route('/delete/user', methods=['POST'])
def deleteUser():
    username = request.form.get('username')
    
    user_deleted = db.users.find_one({'username': username})
    if user_deleted.get('level') == 'Administrator':
        return jsonify({'msg': 'Anda Tidak Dapat Menghapus Administrator'})
    
    user_deleted['delete_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H.%M.%S')
    db.users_deleted.insert_one(user_deleted)
    db.users.delete_one({'username': username})
    return jsonify({'msg': f'Data {username} Berhasil Dihapus'})

@app.route('/recovery/user')
def recoveryUser():
    return render_template('recovery_user.html')

@app.route('/recovery/user', methods=['POST'])
def recovery_user():
    username = request.form.get('username')
    
    data_recovery = db.users_deleted.find_one({'username': username}, {'_id': False})
    result = db.users.insert_one(data_recovery)
    db.users_deleted.delete_one({'username': username})
    if result.acknowledged:
        return jsonify({
            'msg': 'Data Berhasil Dipulihkan'
        })
    else:
        return jsonify({'msg': "Data Gagal Dipulihkan"})

@app.route('/get/recovery', methods=['GET'])
def getRecovery():
    data_recovery = list(db.users_deleted.find({}, {'_id': False}))
    return data_recovery

@app.route('/tracking/actifitys')
def trackingActifities():
    return render_template('track_actifity.html')
    
    
@app.route('/edit/profile')
def edit_profile():
    msg = request.args.get('msg')
    data = db.users.find_one({'username': session['user_name']}, {'_id': False})
    session['email'] = data['email']
    session['user'] = data['name']
    session['profile'] = data['profile']
    return render_template('editProfile.html', msg=msg)

@app.route('/edit/profile', methods=['POST'])
def editProfile():
    name = request.form['name']
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    profile = request.files['profile']
    
    delete_profile = False
    
    if not profile:
        data = db.users.find_one({'username': session['user_name']}, {'_id': False})
        newProfileName = data['profile']
        
    else :
        if not is_valid_image_file(profile.filename):
            return redirect(url_for('edit_profile', msg="Gagal: Yang Anda Upload Bukan Gambar!"))
        else:
            data = db.users.find_one({'username': session['user_name']}, {'_id': False})
            if data['profile'] != 'default_image.jpg' :
                delete_profile = True
                
            currentTime = datetime.datetime.now()
            formatTime = currentTime.strftime('%d-%m-%Y-%H-%M-%S')
            newProfileName = f'profile-{formatTime}.{profile.filename.split(".")[-1]}'
        
    if password:
        updated_user = {
            "$set": {
                "name": html.escape(name),
                "username": html.escape(username),
                "password": html.escape(password),
                "profile": html.escape(newProfileName),
                "email": html.escape(email)
            }
        }
    else:
        updated_user = {
            "$set": {
                "name": html.escape(name),
                "username": html.escape(username),
                "profile": html.escape(newProfileName),
                "email": html.escape(email)
            }
        }

    profile_directory = 'static/image/profile/'
    if not os.path.exists(profile_directory):
        os.makedirs(profile_directory)
            
    pathDestinationProfile = f'{profile_directory}{newProfileName}'
    if profile:
        profile.save(pathDestinationProfile)
        profile_old = db.users.find_one({'username': username}, {'_id': False})
        if delete_profile: 
            if os.path.exists(f'static/image/profile/{profile_old["profile"]}'):
                os.remove(f'static/image/profile/{profile_old["profile"]}')
        
    db.users.update_one({'username': session['user_name']}, updated_user)
    session['user_name'] = username
    return redirect(url_for('edit_profile', msg="Data Berhasil Diperbarui")) 
        
        
    
# globals
# Fungsi validasi ekstensi file gambar
def is_valid_image_file(filename):
    validationExtension = ['jpg', 'png', 'jpeg']
    fileExtension = filename.split('.')[-1].lower()
    return fileExtension in validationExtension


@app.route('/getData', methods=['GET'])
def getUser():

    collection_name = request.args.get('collection')

    collection = db[collection_name]

    data = collection.find({}, {'_id': False})

    user_list = list(data)

    return jsonify({'data': user_list})


@app.route('/delete_folder', methods=['POST'])
def delete_folder():
    foldername = request.form.get('folderName')

    shutil.rmtree(f'file/{foldername}')

    db.file_tugas.delete_one({'fileName': foldername})


    return jsonify({'msg': f'Folder {foldername} Berhasil Dihapus!'})


@app.route('/delete_file', methods=['POST'])
def delete_file():
    file_path = request.form.get('filename')

    try:
        os.remove(f'final_file/{file_path}')  # Menghapus file menggunakan os.remove()
        return jsonify({'msg': f'File {file_path} Berhasil Dihapus!'})
    except Exception as e:
        return jsonify({'msg': str(e)})
    
    
def cek_file_index_html():
    folder_path = 'file_proses'
    
    if os.path.isfile(os.path.join(folder_path, 'index.html')):
        return 'File index.html ditemukan!'
    else:
        return 'File index.html tidak ditemukan.'

@app.route('/getKuis', methods=['GET'])
def getAllKuis():
    nomorKuis = request.args.get('nomorKuis')
    data = list(db.kuis.find({'nomorKuis': nomorKuis}, {'_id': False}))
    return jsonify({
        'data': data
    })
    
@app.route('/getSession', methods=['GET'])
def getSession():
    name = request.args.get('name')
    return session[name]
    
    
def getdataByName(username):
    data = db.users.find_one({'username': username}, {'_id': False})
    return data

def getdataBykey(collection, key, value=None):
    if value is None:
        value = session.get('user_name')  # Mengambil dari session jika None
    collection = db[collection]
    data = collection.find({key: value}, {'_id': False})
    return list(data)


def ekstrak_file(filename):

    # Path arsip yang ingin diekstrak
    path_arsip = f'zipfile/{filename}'

    # Path tujuan ekstraksi
    path_ekstraksi = f'file/{filename.split(".")[0]}'
    
    # Ekstrak arsip
    shutil.unpack_archive(path_arsip, path_ekstraksi)

    os.remove(f'zipfile/{filename}')

@app.route('/download', methods=['POST'])
def modify_and_download():
    username = session['user_name']
    filename = request.form.get('tugas')
    status = request.form.get('status')
    
    doc = ({
        'ip': request.remote_addr,
        'user_agent': request.user_agent.string,
        'device': request.user_agent.platform,
        'browser': request.user_agent.browser,
        'version': request.user_agent.version,
        'id': session['id'],
        'actifity': 'mengerjakan tugas',
        'waktu': datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    })
    db.tracking.insert_one(doc)

    proses_file_tugas(username, filename)
    return redirect(url_for('kerjakan_tugas', username=username, filename=filename, status=status))


def proses_file_tugas(username, filename):

    source_directory = f'file/{filename}'
    destination_directory = 'file_proses'

    user_data = getdataByName(username)

    mongoDbUrl = user_data.get("mongodbUrl")
    dbname = user_data.get("dbname")

    if not os.path.exists(os.path.join(destination_directory, filename)):
        shutil.copytree(source_directory, destination_directory+'/'+filename)
       

    file_path = f'file_proses/{filename}/app.py'

    # Buka file dalam mode baca ('r')
    with open(file_path, 'r') as file:
        content = file.read()

    # Lakukan pengeditan pada konten file
    new_content = content.replace('$', mongoDbUrl).replace('dbname', dbname)

    # Buka file dalam mode tulis ('w') untuk menyimpan konten yang sudah diubah
    with open(file_path, 'w') as file:
        file.write(new_content)

    # Mengarsipkan folder 'file/minggu' menjadi file zip setelah dimodifikasi
    shutil.make_archive(f'final_file/{filename}_{username}', 'zip', 'file_proses', filename)

    folder_path = f'file_proses/'
    shutil.rmtree(destination_directory+'/'+filename)
    

def uniqid():
    return str(uuid.uuid4())


@app.route('/downloads')
def downloads():
    username = session['user_name']
    filename = request.args.get('filename')
    user_agent = request.args.get('user_agent')
    
    doc = ({
        'ip': request.remote_addr,
        'user_agent': user_agent,
        'device': request.user_agent.platform,
        'browser': request.user_agent.browser,
        'version': request.user_agent.version,
        'id': session['id'],
        'actifity': 'mendownlaod tugas',
        'waktu': datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    })
    db.tracking.insert_one(doc)


    p = f'final_file/{filename}_{username}.zip'

    return send_file(p, as_attachment=True, mimetype='application/zip')


@app.route('/download_manual')
def download_manual():

    filename = request.args.get('filename')

    p = f'final_file/{filename}'

    return send_file(p, as_attachment=True, mimetype='application/zip')


# Route untuk registrasi pengguna
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    level = request.form.get('level')
    mongodb_url = request.form.get('mongodb-url')
    dbname = request.form.get('db-name')
    dbname = request.form.get('db-name')

    # Cek apakah pengguna sudah terdaftar
    if db.users.find_one({'username': username}):
        return jsonify({"message": "Username sudah digunakan"})

    # Simpan informasi pengguna ke MongoDB
    db.users.insert_one({
        'username': username,
        'password': password,
        'mongodb_url': mongodb_url,
        'dbname': dbname,
        'level': level
    })

    return jsonify({"message": "Registrasi berhasil"})

# Route untuk login
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    
    # Cari pengguna berdasarkan username dan password
    user = db.users.find_one({'username': username, 'password': password})

    if user:
        user_agent = request.user_agent.string
        doc = ({
            'ip': request.remote_addr,
            'user_agent': user_agent,
            'device': request.user_agent.platform,
            'browser': request.user_agent.browser,
            'version': request.user_agent.version,
            'id': user['id'],
            'actifity': 'login',
            'waktu': datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        })
        db.tracking.insert_one(doc)
        
        session['login'] = True
        session['user_name'] = user['username']
        updateSession()
        return redirect(url_for('index'))
    else:
        return redirect(url_for('view_login', msg='Username Atau Password Salah'))

def updateSession():
    user = db.users.find_one({'username': session['user_name']}, {'_id': False})
    session['user'] = user['name']
    session['id'] = user['id']
    session['level'] = user['level']
    session['user_name'] = user['username']
    session['profile'] = user['profile']
    
@app.route('/login')
def view_login():
    msg = request.args.get('msg')
    return render_template('login.html', msg=msg)

@app.route('/logout', methods=['GET'])
def logout():
    user_agent = request.user_agent.string
    doc = ({
        'ip': request.remote_addr,
        'user_agent': user_agent,
        'device': request.user_agent.platform,
        'browser': request.user_agent.browser,
        'version': request.user_agent.version,
        'id': session['id'],
        'actifity': 'logout',
        'waktu': datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    })
    db.tracking.insert_one(doc)
    session.clear()
    return redirect(url_for('view_login'))

@app.route('/daftar/tugas')
def daftarTugas():
    return render_template('daftar_tugas.html')
    

if __name__ == '__main__':
    app.run('0.0.0.0', port=8080, debug=True)
