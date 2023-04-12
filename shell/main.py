#! /usr/bin/env python3

import os, sys, re

def ch_dir(path):
    try:
        os.chdir(path)
    except:
        os.write(2, "cd: no such file or directory: {}".format(path))
        
def redir1(pid, cmd):

    if pid < 0:
        os.write(2, ("fork failed, returning %d\n" % pid).encode())

    elif pid == 0:
        path = cmd[-1]
        os.close(1)

        try:
            os.open(path, os.O_CREAT | os.O_WRONLY)
            os.set_inheritable(1, True)
        except FileNotFoundError:
            os.write(2, ("%s: No such file or directory" % path).encode())

        cmd = cmd[:cmd.index(">")]

        for dir in re.split(":", os.environ['PATH']):
            prog = "%s/%s" % (dir, cmd[0])

            try:
                os.execve(prog, cmd, os.environ)
            except FileNotFoundError:
                pass

        os.write(2, ("Child: could not exec %s\n" % cmd[0]).encode())
        sys.exit(1)

    else:
        childPidCode = os.wait()


def redir2(pid, cmd):

    if pid < 0:
        os.write(2, ("fork failed, returning %d\n" % pid).encode())
        sys.exit(1)

    elif pid == 0:
        path = cmd[-1]
        os.close(0)
    
        try:
            os.open(path, os.O_CREAT | os.O_RDONLY)
            os.set_inheritable(0, True)
        except FileNotFoundError:
            os.write(2, ("%s: No such file or directory" % path).encode())
            
        cmd = cmd[:cmd.index("<")]

        for dir in re.split(":", os.environ['PATH']):
            prog = "%s/%s" % (dir, cmd[0])

            try:
                os.execve(prog, cmd, os.environ)
            except FileNotFoundError:
                pass

        os.write(2, ("Child: could not exec %s\n" % cmd[0]).encode())
        sys.exit(1)

    else:
        childPidCode = os.wait()

        
                
def myPipe(cmd):
    pr, pw = os.pipe()
    
    pid1 = os.fork()
    
    if pid1 == 0:
        os.close(pr)
        os.dup2(pw, 1)
        os.close(pw)

        cmd1 = cmd[:cmd.index("|")]

        for dir in re.split(":", os.environ['PATH']):
            prog1 = "%s/%s" % (dir, cmd1[0])

            try:
                os.execve(prog1, cmd1, os.environ)
            except FileNotFoundError:
                pass
            
    pid2 = os.fork()
        
    if pid2 == 0:
        os.close(pw)
        os.dup2(pr, 0)
        os.close(pr)

        cmd2 = cmd[cmd.index("|")+1:]

        for dir in re.split(":", os.environ['PATH']):
            prog2 = "%s/%s" % (dir, cmd2[0])

            try:
                os.execve(prog2, cmd2, os.environ)
            except FileNotFoundError:
                pass
            

    os.close(pr)
    os.close(pw)
    os.waitpid(pid1,0)
    os.waitpid(pid2,0)
    

def progExec(pid, args):
    if pid < 0:
        os.write(2, ("fork failed, returning %d\n" % pid).encode())
        sys.exit()

    elif pid == 0:
        for dir in re.split(":", os.environ['PATH']):
            prog = "%s/%s" % (dir, args[0])

            try:
                os.execve(prog, args, os.environ)
            except FileNotFoundError:
                pass

        os.write(2, "Child: could not exec %s\n" % args[0].encode())
        sys.exit(1)

    else:
        childPidCode = os.wait()





while True:
    path = os.getcwd() +  "/$ "
    os.write(1, path.encode())

    cmd = os.read(0, 1000).decode().split()


    if cmd[0] == "exit":
        os.write(1, "exting myShell...\n".encode())
        sys.exit()
        
    elif cmd[0] == "cd":
        ch_dir(cmd[1])

    
    #TESTING

    else:
        
        if "|" in cmd:
            myPipe(cmd)

        elif ">" in cmd:
            rc = os.fork()
            redir1(rc, cmd)

        elif "<" in cmd:
            rc = os.fork()
            redir2(rc, cmd)
            
        rc = os.fork()
        progExec(rc, cmd)