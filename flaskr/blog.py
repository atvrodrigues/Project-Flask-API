from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    """Mostra todos os alunos por ordem de UID"""
    db = get_db()
    posts = db.execute(
        'SELECT usuario, uidNumber, nome, home, grupoBase, matricula,grupoSecundario,senha'
        ' FROM aluno '
        ' ORDER BY uidNumber ASC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/criar', methods=('GET', 'POST'))
def create():
    """Criar novo aluno"""
    if request.method == 'POST':
        usuario = request.form['usuario']
        uidNumber = request.form['uidNumber']
        nome = request.form['nome']
        home = request.form['home']
        grupoBase = request.form['grupoBase']
        matricula = request.form['matricula']
        grupoSecundario = request.form['grupoSecundario']
        senha = request.form['senha']

        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO aluno (usuario, uidNumber, nome, home, grupoBase, matricula, grupoSecundario, senha)'
                ' VALUES (?, ?, ?, ?, ?, ?, ? )',
                (usuario, uidNumber, nome, home, grupoBase, matricula, grupoSecundario, senha)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(key):
    aluno = get_db().execute(
        'SELECT usuario, uidNumber, nome, home, grupoBase, matricula, grupoSecundario, senha'
        ' FROM aluno '
        ' WHERE  uidNumber = ?',
        (key,)
    ).fetchone()

    if aluno is None:
        abort(404, "Uid do usuário não existe.".format(id))

    return aluno


@bp.route('/<int:uidNumber>/atualizar', methods=('GET', 'POST'))
def update(uidNumber):
    aluno = get_post(uidNumber)
    if request.method == 'POST':
        usuario = request.form['usuario']
        uidNumber = request.form['uidNumber']
        nome = request.form['nome']
        home = request.form['home']
        grupoBase = request.form['grupoBase']
        matricula = request.form['matricula']
        grupoSecundario = request.form['grupoSecundario']
        senha = request.form['senha']

        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(

                'UPDATE aluno SET usuario = ?, nome = ?, home = ?, grupoBase = ?, matricula = ?, uidNumber = ?, grupoSecundario = ?, senha = ?'
                'WHERE uidNumber = ?',
                (usuario, nome, home, grupoBase, matricula, uidNumber, uidNumber, grupoSecundario, senha)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=aluno)


@bp.route('/<int:uidNumber>/deletar', methods=('POST',))
def delete(uidNumber):
    """Deleta aluno e suas informações caso exista"""
    
    get_post(uidNumber)
    db = get_db()
    db.execute('DELETE FROM aluno WHERE uidNumber = ?', (uidNumber,))
    db.commit()
    return redirect(url_for('blog.index'))
