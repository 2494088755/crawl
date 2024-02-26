from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/music'
db = SQLAlchemy(app)

# 定义模型
class TbMusic(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    song_name = db.Column(db.String(255))
    download_url = db.Column(db.Text)
    singer_name = db.Column(db.String(255))


# 首页
@app.route('/')
def index():
    songs = TbMusic.query.all()
    return render_template('index.html', songs=songs)

# 添加歌曲
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        song_name = request.form['song_name']
        download_url = request.form['download_url']
        singer_name = request.form['singer_name']
        song = TbMusic(song_name=song_name, download_url=download_url, singer_name=singer_name)
        db.session.add(song)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html')

# 删除歌曲
@app.route('/delete/<int:id>')
def delete(id):
    song = TbMusic.query.get_or_404(id)
    db.session.delete(song)
    db.session.commit()
    return redirect(url_for('index'))

# 修改歌曲
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    song = TbMusic.query.get_or_404(id)
    if request.method == 'POST':
        song.song_name = request.form['song_name']
        song.download_url = request.form['download_url']
        song.singer_name = request.form['singer_name']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', song=song)

if __name__ == '__main__':
    app.run()
