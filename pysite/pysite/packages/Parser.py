#!/usr/bin/env python
#encoding=utf-8

# 导入规则表达式模块
import re

class Group:
    ''' 权限用户组对象
    属性：
        name(string)表示组名称；
        users(list)表示成员列表。'''

    def __init__(self, name=''):
        ''' 构造函数，name参数可选。 '''
        self.name = name
        self.users = []

class Auth:
    ''' 权限对象
    属性：
        name(string)表示权限名称，r,w,rw；
        users(list)表示成员列表。'''
        
    def __init__(self, name=''):
        ''' 构造函数，name参数可选。 '''
        self.name = name
        self.users = []

class DirAuth:
    ''' 路径权限对象
    属性：
        name(string)表示组名称
        auths(list)表示权限对象列表。'''

    def __init__(self, name=''):
        ''' 构造函数，name参数可选。'''
        self.name = name
        self.auths = []
        
class Parser:
    ''' 解析器对象
    属性：
        filename(string)文件全名；
        groups(list)权限用户组对象；
        dirs(list)路径权限对象DirAuth列表；
    方法：
        load，读取文件；
        save，覆写文件。'''
    
    def __init__(self, filename=''):
        ''' 构造函数，filename参数可选。'''
        self.filename = filename
        self.groups = []
        self.dirs = []
        
    def __add_dir(self, dirname):
        ''' 根据名称向dirs表中添加一个DirAuth对象，并返回该对象；
        如名称已存在，不添加直接返回该对象。'''
        # 检索现有列表
        for d in self.dirs:
            if d.name == dirname:
                return d
        d = DirAuth(dirname)
        self.dirs.append(d)
        return d
        
    def __add_group(self, groupname):
        ''' 根据名称向dirs表中添加一个Group对象，并返回该对象；
        如名称已存在，不添加直接返回该对象。'''
        # 检索现有列表
        for g in self.groups:
            if g.name == groupname:
                return g
        g = Group(groupname)
        self.groups.append(g)
        return g
        
    def load(self, filename=''):
        ''' 读取并解析文件，解析内容保存到本对象'''
        if filename: self.filename = filename
        # 读取权限访问的配置文件
        f = open(self.filename, 'r')
        # 读入字符串
        fstring = f.read()
        f.close()
        # 解析字符串
        self.fromString(fstring)

    def fromString(self, fstring):
        # 清除对象现有内容
        self.groups = []
        self.dirs = []

        # 转为按行的字串列表
        ls = fstring.replace('\r', '').split('\n')

        # 去掉#的注释
        ls = [re.sub(r'#.*$','',l) for l in ls]

        # 去掉空白
        ls = [l.replace(' ','') for l in ls if l]

        # 去掉空行
        ls = [l for l in ls if l]

        # 解析使用的变量初始化
        status = 0      # 状态机的状态值
        cur_dir = ''    # 当前的权限路径对象

        # 逐行解析处理，使用规则表达式匹配；使用状态机
        for i in range(len(ls)):

            # 初始状态，可转入1：分组group项定义块，或2：目录访问权限定义块
            if status == 0:
                # 匹配到[group]时，进入状态1
                if re.search(r'^\[groups\]$', ls[i]):
                    status = 1
                # 匹配到[/xxxx]时，表示路径，进入状态2
                elif re.search(r'^\[/[\w\.\-_]*\]$', ls[i]):
                    status = 2
                    cur_dir = self.__add_dir(ls[i])
                # 其他情况，不合理的异常情况，不处理
                else: pass

            # 进入group定义块，可转入2
            elif status == 1:
                # 匹配“xxx=yyy[,zzz]”模式
                if re.search(r'^[A-Za-z][\w\.\-_]*=[A-Za-z][\w\.\-_]*', ls[i]):
                    # 分解为['xxx', 'yyy,zzz'],xxx为组名称
                    tokens = ls[i].split('=')
                    g = self.__add_group(tokens[0])
                    # 继续分解并添加到成员列表
                    g.users.extend(tokens[1].split(','))
                # 同status0是的匹配，[/xxxx]时，表示路径，进入状态2
                elif re.search(r'^\[/[\w\.\-_]*\]$', ls[i]):
                    status = 2
                    cur_dir = self.__add_dir(ls[i])
                else: pass

            # 进入各路径的权限定义块，包含一组路径的配置
            elif status == 2:
                # 匹配到[group]时，进入状态1
                if re.search(r'^\[groups\]$', ls[i]):
                    status = 1
                # [/xxxx]时，表示新的路径
                elif re.search(r'^\[/[\w\.\-_]*\]$', ls[i]):
                    cur_dir = self.__add_dir(ls[i])
                # 匹配“yyy[,zzz]=rw”模式
                elif re.search(r'^[A-Za-z\*][\w\.\-_]*=[rw]{1,2}$', ls[i]):
                    # 分解为['yyy,zzz','rw']
                    tokens = ls[i].split('=')
                    # 根据本行内容创建Auth对象，并添加到当前dir的auths列表
                    auth = Auth(tokens[1])
                    cur_dir.auths.append(auth)
                    auth.users.extend(tokens[0].split(','))
                # 匹配“@yyy[,zzz]=rw”模式
                elif re.search(r'^@[A-Za-z\*][\w\.\-_]*=[rw]+$', ls[i]):
                    # 分解为['@yyy,@zzz','rw']
                    tokens = ls[i].split('=')
                    # 根据本行内容创建Auth对象，并添加到当前dir的auths列表
                    auth = Auth(tokens[1])
                    cur_dir.auths.append(auth)
                    auth.users.extend(tokens[0].split(','))
                # 其他情况，不处理
                else: pass
    def toString(self):
        ''' 将对象内容输出为字符串，字符串格式与文件一致，可直接存为文件 '''
        import StringIO
        f = StringIO.StringIO()
        # 写入说明信息
        f.write('# Auto generate by SVNAuth.py\n\n')

        # 写入组成员信息
        if len(self.groups) > 0:
            f.write('[groups]\n')
        for g in self.groups:
            f.write(' = '.join([g.name, ', '.join(g.users)]))
            f.write('\n')
        f.write('\n')

        # 写入路径权限信息
        for d in self.dirs:
            f.write(d.name + '\n')
            for a in d.auths:
                f.write(' = '.join([', '.join(a.users), a.name]))
                f.write('\n')

        fstring = f.getvalue()
        f.close()
        return fstring

    def save(self, filename=''):
        ''' 将本对象的内容保存到文件，不指定文件名时，保存到读取的原文件'''
        if filename == '': filename = self.filename
            
        # 读取权限访问的配置文件
        f = open(filename, 'w')
        # 写入文件
        fstring = self.toString()
        f.write(fstring)
        f.close()
        
    
    def printobj(self):
        ''' 打印本对象的内容'''
        print 'filename: ', self.filename
        for g in self.groups:
            print 'group: ', g.name, 'users: ', g.users
        for d in self.dirs:
            print 'dirname: ', d.name
            for a in d.auths:
                print '  # authname:', a.name, 'users: ', a.users
    
if __name__ == "__main__":
    p = Parser('access')
    p.load()
    p.printobj()
    p.save('access1')
    
        
