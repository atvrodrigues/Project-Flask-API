#!/usr/bin/env python3

import ldap3
import sys


class LdapBase:
    url = 'ldap.inf.ufsm.br'
    usuarios = 'ou=People,dc=inf,dc=ufsm,dc=br'
    grupos = 'ou=Group,dc=inf,dc=ufsm,dc=br'    
    
    def __init__(self):
        self.server = ldap3.Server(LdapBase.url, get_info=ldap3.ALL)

    def buscaLogin(self, login, campos=ldap3.ALL_ATTRIBUTES):
        res = self.conn.search( LdapBase.usuarios,
                          '(uid={0})'.format(login),
                          attributes=campos )
        if res: return self.conn.entries[0]
        else: return None

    def listaUsuarios(self, campos=ldap3.ALL_ATTRIBUTES):
        res = self.conn.search( LdapBase.usuarios,
                                '(uid=*)',
                                attributes=campos )
        if res: return self.conn.entries
        else: return None

    def buscaGrupo(self, grupo, campos=ldap3.ALL_ATTRIBUTES):
        res = self.conn.search( LdapBase.grupos,
                                '(cn={0})'.format(grupo),
                                attributes=campos )
        if res: return self.conn.entries[0]
        else: return None

    def listaGrupos(self, campos=ldap3.ALL_ATTRIBUTES):
        res = self.conn.search( LdapBase.grupos,
                                '(cn=*)',
                                attributes=campos )
        if res: return self.conn.entries
        else: return None

    # TODO
    def buscaNome(self, nome): pass

    def buscaGidGrupo(self, grupo):
        res = self.conn.search( LdapBase.grupos,
                                '(cn={0})'.format(grupo),
                                attributes=[ 'gidNumber' ] )
        if not res:
            return -1
        return self.conn.entries[0]['gidNumber']
        
    def buscaNovoUid(self):
        res = self.conn.search( LdapBase.usuarios,
                                '(uid=*)',
                                attributes=[ 'uidNumber' ] )
        if not res:
            return -1
        entradas = [ a.uidNumber.value for a in self.conn.entries ]
        entradas.sort()
        return ( entradas[-1] + 1 )
    
    def buscaNovoGid(self):
        res = self.conn.search( LdapBase.grupos,
                                '(gidNumber=*)',
                                attributes=[ 'gidNumber' ] )
        if not res:
            return -1
        entradas = [ a.gidNumber.value for a in self.conn.entries ]
        entradas.sort()        
        return ( entradas[-1] + 1 )

class Ldap(LdapBase):
    def __init__(self):
        LdapBase.__init__(self)
        self.conn = ldap3.Connection(self.server, auto_bind=True)

    def fecha(self):
        self.conn.unbind()
        
class LdapAdmin(LdapBase):
    admin = 'cn=admin,dc=inf,dc=ufsm,dc=br'
    senha = 'cyzvinEw3'

    def __init__(self):
        LdapBase.__init__(self)
        self.conn = ldap3.Connection(self.server, LdapAdmin.admin,
                                     LdapAdmin.senha,
                                     auto_bind=True)

    def adicionaUsuario(self,
                        login, nome,
                        grupo='outros', aluno=True,
                        matricula=0, email=None,
                        curso='CC' ):
        # quebra nome por espaços
        nomes = nome.split()
        # entrada LDAP do usuário
        alvo = "uid={0},{1}".format(login, LdapBase.usuarios)
        # atributos do usuário
        atributos = {}
        atributos['uid'] = login
        atributos['cn'] = nome
        atributos['loginShell'] = '/bin/bash'
        atributos['uidNumber'] = self.buscaNovoUid()
        atributos['gidNumber'] = self.buscaGidGrupo(grupo)
        if aluno:
            atributos['homeDirectory'] = '/home/alunos/{0}'.format(login)
        else:
            atributos['homeDirectory'] = '/home/profs/{0}'.format(login)
        atributos['gecos'] = nome
        atributos['objectClass'] = ['top', 'posixAccount', 'shadowAccount',
                                    'inetOrgPerson']
        atributos['shadowLastChange'] = -1
        atributos['shadowMin'] =  0
        atributos['shadowMax'] = 99999
        atributos['shadowInactive'] =  -1
        atributos['shadowWarning'] = 7
        atributos['shadowExpire'] = 99999
        atributos['shadowFlag'] = -1
        atributos['description'] = -1
        # novos campos
        if email == None:
            atributos['mail'] = '{0}.inf.ufsm.br'.format(login) 
        else:
            atributos['mail'] = email            
        atributos['displayName'] = nomes[0]
        atributos['employeeNumber'] = matricula
        atributos['employeeType'] = 'Pessoa'
        atributos['o'] = 'UFSM' # organizationName
        atributos['ou'] = curso # organizationalUnitName
        atributos['l'] = 'Santa Maria, RS, BR' # localityName
        atributos['sn'] = nomes[-1] # surname
        atributos['initials'] = ''.join([c[0].upper() for c in nomes])
        #atributos[''] = ''
        #print(str(atributos))
        res = self.conn.add( alvo, attributes=atributos )
        return res

    
    def adicionaGrupo(self, grupo):
        alvo = "cn={0},{1}".format(grupo, LdapBase.grupos)        
        atributos = {}
        atributos['cn'] = grupo
        atributos['gidNumber'] = self.buscaNovoGid()
        atributos['objectClass'] = ['top', 'posixGroup']
        atributos['userPassword'] = '{cript}'
        #print(str(atributos))
        res = self.conn.add( alvo, attributes=atributos )
        return res

    def mudaSenha(self, login, senha):
        alvo = "uid={0},{1}".format(login, LdapBase.usuarios)        
        hashed_pass = ldap3.utils.hashed.hashed(
            ldap3.HASHED_SALTED_SHA, senha)
        atributos = {}
        atributos['userPassword'] = [(ldap3.MODIFY_REPLACE, [hashed_pass])]
        #print(str(atributos))
        res = self.conn.modify( alvo, atributos )
        return res

        
    def mudaHome(self, login, home): pass

    
if __name__ == "__main__":

    print('\nERRO: nao use para testes!\n')
    sys.exit()

    # testes LDAP não privilegiado
    x = Ldap()
    info = x.buscaLogin('jvlima')
    if info is not None:
        print('buscaLogin Ok')

    info = x.buscaGrupo('inf2013')
    if info is not None:
        print('buscaGrupo Ok')

    info = x.listaUsuarios()
    if info is not None:
        print('listaUsuarios Ok')

    info = x.listaGrupos()
    if info is not None:
        print('listaGrupos Ok')

    info = x.buscaGidGrupo('inf2013')
    if info != -1:
        print('buscaGidGrupo Ok (' + str(info) + ')')

    info = x.buscaNovoUid()
    if info != -1:
        print('buscaNovoUid Ok (' + str(info) + ')')

    info = x.buscaNovoGid()
    if info != -1:
        print('buscaNovoGid Ok (' + str(info) + ')')

    x.fecha()
#    print(str(info))

    x = LdapAdmin()
    info = x.adicionaGrupo('zoeira')
    if info == True:
        print('adicionaGrupo Ok')
    else:
        print('adicionaGrupo ERRO')
        sys.exit()

    info = x.adicionaUsuario(login='xabunfoa', nome='Xabunfo Bugio', grupo='zoeira',
                             aluno=True, matricula=2014661111, email='zoeira@gmail.com',
                             curso='CC')
    if info == True:
        print('adicionaUsuario Ok')
    else:
        print('adicionaUsuario ERRO')
        sys.exit()
    
    info = x.mudaSenha('xabunfoa', 'nada')
    if info == True:
        print('mudaSenha Ok')
    else:
        print('mudaSenha ERRO')
        sys.exit()

    
    #testes LDAP privilegiado
