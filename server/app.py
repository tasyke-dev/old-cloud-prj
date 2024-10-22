import subprocess
import math
import os
import uuid
import shutil
import PIL
from werkzeug.utils import secure_filename
from flask import Flask, request, abort, jsonify, url_for
from flask_mongoengine import MongoEngine
from flask_cors import CORS

UPLOAD_FOLDER = os.getcwd()
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
ALLOWED_PHOTONOTES_EXTENSIONS = {'png', 'jpg', 'jpeg'}
windows = './poppler-0.68.0/bin/pdftocairo.exe'
ubuntu = 'pdftocairo'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app)
app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb+srv://root:123123123@cluster0.04w4x.mongodb.net/leaf?retryWrites=true&w=majority'
}
db = MongoEngine()
db.init_app(app)

def popplerCall(args):
    return subprocess.call(args)

def createTiles(zooms, image, dir):
    # subprocess.call(['export', 'GDAL_ALLOW_LARGE_LIBJPEG_MEM_ALLOC=1'])
    return subprocess.call(['python3', 'gdal2tiles.py', '-l', '-p', 'raster', '-z', zooms, '-w', 'none', image, dir])

class Notes(db.EmbeddedDocument):
    coords = db.ListField(db.FloatField())
    text = db.StringField()

class PhotoNotes(db.EmbeddedDocument):
    coords = db.ListField(db.FloatField())
    path = db.StringField()

class Polygons(db.EmbeddedDocument):
    coords = db.ListField(db.ListField(db.FloatField()))
    color = db.StringField()
    text = db.StringField()

class Images(db.EmbeddedDocument):
    path = db.StringField()
    maxZoom = db.StringField()
    pageNumber = db.StringField()
    notes = db.ListField(db.EmbeddedDocumentField(Notes))
    photoNotes = db.ListField(db.EmbeddedDocumentField(PhotoNotes))
    polygons = db.ListField(db.EmbeddedDocumentField(Polygons))

class Pdfs(db.Document):
    filename = db.StringField()
    folderName = db.StringField()
    images = db.ListField(db.EmbeddedDocumentField(Images))

def make_images_object(path, maxZoom, pageNumber, notes=None, photoNotes=None, polygons=None):
    images = Images()
    images.path = path
    images.maxZoom = maxZoom
    images.pageNumber = str(pageNumber)
    images.notes = notes
    images.photoNotes = photoNotes
    images.polygons = polygons
    return images

def make_notes_object(coords, text):
    notes = Notes()
    notes.coords = coords
    notes.text = text
    return notes

def make_photonotes_object(coords, path):
    photoNotes = PhotoNotes()
    photoNotes.coords = coords
    photoNotes.path = path
    return photoNotes

def make_polygons_object(coords, color, text):
    polygons = Polygons()
    polygons.coords = coords
    polygons.color = color
    polygons.text = text
    return polygons

def allowed_file(filename, extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in extensions

@app.route('/api/pdf', methods=['POST'])
def convert_pdf():
    if not request.form['dpi'] and not request.files['file']:
        abort(400)
    isPdf = False
    file = request.files['file']
    if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        if filename.split('.')[1] == 'pdf':
            isPdf = True
    else:
        abort(400)
    path = os.path.join(os.path.join(os.path.dirname(os.getcwd()), 'data'), str(uuid.uuid4().hex))
    os.mkdir(path)
    images = []
    imagesWithZooms = []
    # TODO: Поиск текста с картинки
    # argsToText = ['./poppler-0.68.0/bin/pdftotext.exe', './out.pdf', './test.doc']
    if isPdf:
        if request.form.get("pages", False):
            for page in request.form["pages"].split(','):
                argsToImages = [ubuntu, filename, '-jpeg', '-r', request.form['dpi'], '-f', page, '-l', page]
                popplerCall(argsToImages)
        elif request.form.get("from", False) and request.form.get("to", False):
            argsToImages = [ubuntu, filename, '-jpeg', '-r', request.form['dpi'], '-f', request.form['from'], '-l', request.form['to']]
            popplerCall(argsToImages)
        else:
            argsToImages = [ubuntu, filename, '-jpeg', '-r', request.form['dpi']]
            popplerCall(argsToImages)
        for filename in os.listdir(os.getcwd()):
            if filename.endswith('.jpg'):
                shutil.move(os.path.join(os.getcwd(), filename), os.path.join(path, filename))
                images.append(str(os.path.join(path, filename)))
            elif filename.endswith('.png'):
                shutil.move(os.path.join(os.getcwd(), filename), os.path.join(path, filename))
                images.append(str(os.path.join(path, filename)))
            elif filename.endswith('.jpeg'):
                shutil.move(os.path.join(os.getcwd(), filename), os.path.join(path, filename))
                images.append(str(os.path.join(path, filename)))
            elif filename.endswith('.pdf'):
                shutil.move(os.path.join(os.getcwd(), filename), os.path.join(path, filename))
        for index, imagePath in enumerate(images):
            image = PIL.Image.open(imagePath)
            width, height = image.size
            maxZoom = str(math.ceil(math.log2(max(width, height)/256)))
            zoom = '0-' + maxZoom
            createTiles(zoom, imagePath, os.path.join(path, str(index)))
            imagesWithZooms.append(make_images_object(os.path.join(path, str(index)), maxZoom, imagePath.split('-')[1].split('.')[0]))
    else:
        shutil.move(os.path.join(os.getcwd(), filename), os.path.join(path, filename))
        images.append(str(os.path.join(path, filename)))
        for index, imagePath in enumerate(images):
            image = PIL.Image.open(imagePath)
            width, height = image.size
            maxZoom = str(math.ceil(math.log2(max(width, height)/256)))
            zoom = '0-' + maxZoom
            createTiles(zoom, imagePath, os.path.join(path, str(index)))
            imagesWithZooms.append(make_images_object(os.path.join(path, str(index)), maxZoom, 0))
    Pdfs(filename=request.files['file'].filename, folderName=path, images=imagesWithZooms).save()
    return jsonify({'filename': request.files['file'].filename, 'folderName': path, 'images': imagesWithZooms}), 201

@app.route('/api/update', methods=['PUT'])
def update_all():
    if not request.json['images']:
        abort(400)
    pages = Pdfs.objects().get(pk=request.json['_id']['$oid'])
    if not pages:
        abort(400)
    images = []
    notes = []
    photoNotes = []
    polygons = []
    for index, i in enumerate(request.json['images']):
        for index, j in enumerate(i['notes']):
            notes.append(make_notes_object(j['coords'], j['text']))
        for index, j in enumerate(i['photoNotes']):
            photoNotes.append(make_photonotes_object(j['coords'], j['path']))
        for index, j in enumerate(i['polygons']):
            polygons.append(make_polygons_object(j['coords'], j['color'], j['text']))
        images.append(make_images_object(i['path'], i['maxZoom'], i['pageNumber'], notes, photoNotes, polygons))
        notes = []
        photoNotes = []
        polygons = []
    Pdfs.objects(pk=request.json['_id']['$oid']).update(
        set__images = images
    )
    return jsonify(images), 200

@app.route('/api/notes', methods=['POST'])
def update_notes():
    if not request.json['id'] and not request.json['coords'] and not request.json['text'] and not request.json['pageNumber']:
        abort(400)
    pages = Pdfs.objects().get(pk=request.json['id'])
    images = []
    notes = []
    for index, i in enumerate(pages.images):
        if i.pageNumber == request.json['pageNumber']:
            if (pages.images[index].notes):
                for k in pages.images[index].notes:
                    notes.append(make_notes_object(k.coords, k.text))
            notes.append(make_notes_object(request.json['coords'], request.json['text']))
            images.append(make_images_object(i.path, i.maxZoom, i.pageNumber, notes, i.photoNotes, i.polygons))
        else: images.append(make_images_object(i.path, i.maxZoom, i.pageNumber, i.notes, i.photoNotes, i.polygons))
    Pdfs.objects(pk=request.json['id']).update(
        set__images = images
    )
    return jsonify(images), 200

@app.route('/api/photonotes', methods=['POST'])
def update_photonotes():
    if not request.form['id'] and not request.files['file'] and not request.form['coords'] and not request.form['pageNumber']:
        abort(400)
    file = request.files['file']
    if file and allowed_file(file.filename, ALLOWED_PHOTONOTES_EXTENSIONS):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        abort(400)
    pages = Pdfs.objects().get(pk=request.form['id'])
    coords = request.form['coords'].split('[')[1].split(']')[0].split(',')
    for index, i in enumerate(coords):
        coords[index] = float(i)
    images = []
    photoNotes = []
    imagePath = ""
    path = os.path.join(os.path.join(os.path.dirname(os.getcwd()), 'data'), 'photos')
    if not os.path.exists(path):
        os.mkdir(path)
    for filename in os.listdir(os.getcwd()):
        if filename.endswith('.jpg'):
            uniqueFilename = str(uuid.uuid4().hex) + '.jpg'
            shutil.move(os.path.join(os.getcwd(), filename), os.path.join(path, uniqueFilename))
            imagePath = str(os.path.join(path, uniqueFilename))
        elif filename.endswith('.jpeg'):
            uniqueFilename = str(uuid.uuid4().hex) + '.jpeg'
            shutil.move(os.path.join(os.getcwd(), filename), os.path.join(path, uniqueFilename))
            imagePath = str(os.path.join(path, uniqueFilename))
        elif filename.endswith('.png'):
            uniqueFilename = str(uuid.uuid4().hex) + '.png'
            shutil.move(os.path.join(os.getcwd(), filename), os.path.join(path, uniqueFilename))
            imagePath = str(os.path.join(path, uniqueFilename))
    for index, i in enumerate(pages.images):
        if i.pageNumber == request.form['pageNumber']:
            if (pages.images[index].photoNotes):
                for k in pages.images[index].photoNotes:
                    photoNotes.append(make_photonotes_object(k.coords, k.path))
            photoNotes.append(make_photonotes_object(coords, imagePath))
            images.append(make_images_object(i.path, i.maxZoom, i.pageNumber, i.notes, photoNotes, i.polygons))
        else: images.append(make_images_object(i.path, i.maxZoom, i.pageNumber, i.notes, i.photoNotes, i.polygons))
    Pdfs.objects(pk=request.form['id']).update(
        set__images = images
    )
    return jsonify(images), 200

@app.route('/api/polygons', methods=['POST'])
def update_polygons():
    if not request.json['id'] and not request.json['coords'] and not request.json['text'] and not request.json['color'] and not request.json['pageNumber']:
        abort(400)
    pages = Pdfs.objects().get(pk=request.json['id'])
    images = []
    polygons = []
    for index, i in enumerate(pages.images):
        if i.pageNumber == request.json['pageNumber']:
            if (pages.images[index].polygons):
                for k in pages.images[index].polygons:
                    polygons.append(make_polygons_object(k.coords, k.color, k.text))
            polygons.append(make_polygons_object(request.json['coords'], request.json['color'], request.json['text']))
            images.append(make_images_object(i.path, i.maxZoom, i.pageNumber, i.notes, i.photoNotes, polygons))
        else: images.append(make_images_object(i.path, i.maxZoom, i.pageNumber, i.notes, i.photoNotes, i.polygons))
    Pdfs.objects(pk=request.json['id']).update(
        set__images = images
    )
    return jsonify(images), 200

@app.route('/api', methods=['GET'])
def get_pages():
    pages = Pdfs.objects()
    if not pages:
        return jsonify({'error': 'data not found'})
    else:
        return jsonify(pages)

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0')