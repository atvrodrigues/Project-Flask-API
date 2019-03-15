import sqlite3
import sys
from flaskr import ncc
from ldap3.core.exceptions import LDAPCursorError
import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    """Clear existing data and create new tables."""
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def dadosBasicoAlunoNcc():
    db = get_db()
    x = ncc.Ldap()
    res = x.listaUsuarios()
    if res is None:
        print('\nERRO: nao foi possivel listar usuarios!\n')
        sys.exit()
    for e in res:
        if e.uidNumber != 3432:
            db.execute(
                'INSERT INTO aluno (usuario, uidNumber, nome, home, grupoBase)'
                'VALUES (?,?,?,?,?)',
                (e.uid.value, e.uidNumber.value, e.gecos.value, e.homeDirectory.value, e.gidNumber.value)
            )
            db.commit()
    x.fecha()
    print(
        "Usuários, UID, nomes e homes atualizados. \n"

    )


def matriculaAlunoNcc():
    db = get_db()
    x = ncc.Ldap()
    res = x.listaUsuarios()
    for e in res:
        if e.uidNumber != 3432:
            try:
                db.execute(
                    'UPDATE aluno SET matricula = ?'
                    'WHERE usuario = ?',
                    (e.employeeNumber.value, e.uid.value)

                )
                db.commit()
            except LDAPCursorError:
                pass
    x.fecha()
    print(
        "Matriculas atualizadas. \n"
    )


def emailAlunoNcc():
    db = get_db()
    x = ncc.Ldap()
    res = x.listaUsuarios()
    for e in res:
        if e.uidNumber != 3432:
            try:
                db.execute('UPDATE aluno SET email = ?'
                 'WHERE usuario = ?', (e.mail.value, e.uid.value))
                db.commit()
            except LDAPCursorError:
                pass
    x.fecha()
    print(
        "Emails atualizados. \n"
    )


def senhaAlunoNcc():
    db = get_db()
    x = ncc.Ldap()
    res = x.listaUsuarios()
    for e in res:
        if e.uidNumber != 3432:
            try:
                aux = str(e.userPassword.value)
                aux = aux.replace("b'{ssha}", "")
                aux = aux.replace("=='", "")
                db.execute('UPDATE aluno SET senha = ?'
                          'WHERE usuario = ?', (aux, e.uid.value))
                db.commit()
            except LDAPCursorError:
                pass
    x.fecha()
    print(
        "Senhas atualizadas. \n"
    )


def grupoSecundarioAlunoNcc():
    db = get_db()
    x = ncc.Ldap()
    res = x.listaGrupos()
    for e in res:
        try:
            aux = str(e.memberUid.value)
            aux = aux.replace("[", "")
            aux = aux.replace("]", "")
            aux = aux.replace("'", "")
            db.execute('UPDATE aluno SET grupoSecundario = ?'
                       'WHERE grupoBase = ?', (aux, e.gidNumber.value))
            db.commit()
        except LDAPCursorError:
            pass
    x.fecha()
    print(
        "Grupos Secudários atualizados. \n"
    )


def grupoBaseAlunoNcc():
    db = get_db()
    x = ncc.Ldap()
    res = x.listaGrupos()
    for e in res:
        try:
            db.execute('UPDATE aluno SET grupoBase = ?'
             'WHERE grupoBase = ?', (e.cn.value, e.gidNumber.value))
            db.commit()
        except LDAPCursorError:
            pass
    db.close()
    x.fecha()
    print(
        "Grupos Base atualizados. \n"
    )


@click.command('atualizar')
@with_appcontext
def atualizar():
    # Zera Banco de Dados e reestabelece as tables
    init_db()
    dadosBasicoAlunoNcc()
    matriculaAlunoNcc()
    emailAlunoNcc()
    senhaAlunoNcc()
    grupoSecundarioAlunoNcc()
    grupoBaseAlunoNcc()
    print("\n PRONTO!")


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(atualizar)
