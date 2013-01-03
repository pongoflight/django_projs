from django.shortcuts import render_to_response

def svnauth(request):
    from pysite.packages import Parser
    p = Parser.Parser()
    p.load('/home/wlx/projects/svn_admin/access')
    return render_to_response('svnauth.html', {'groups':p.groups, 'dirs':p.dirs})
