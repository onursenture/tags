import os
import fnmatch
import shutil


# -----------------------------------------------------------------------------
# Exceptions
# -----------------------------------------------------------------------------

class TagErrorArguments(Exception):
    def __init__(self, tagname, nargs, args):
        params = (tagname, nargs, u" ".join(args))
        errstr = u"malformed tag '{0}' should have {1} argument(s), got '{2}'"
        self.msg = errstr.format(*params)

    def __str__(self):
        return self.msg


class TagErrorBody(Exception):
    def __init__(self, tagname, req_body, has_body):
        req = u'' if req_body else u"n't"
        has = u'does' if has_body else u"doesn't"
        params = (tagname, req, has)
        errstr = u"malformed tag '{0}' should{1} have a body, but {2}"
        self.msg = errstr.format(*params)

    def __str__(self):
        return self.msg


# -----------------------------------------------------------------------------
# Decorators
# -----------------------------------------------------------------------------

def checktag(num_args=None, is_block=None):
    '''
    Does error checking for a tag, raising an error if the 
    tag is called with incorrect argument count or body
    '''
    def _decorator(fn):
        def _wrapper(args, context, **kwargs):
            if num_args != None and len(args) != num_args:
                raise TagErrorArguments(fn.__name__, num_args, args)
            has_body = 'body' in kwargs
            if is_block != None and has_body != is_block:
                raise TagErrorBody(fn.__name__, is_block, has_body)
            return fn(args, context, **kwargs)
        return _wrapper
    return _decorator


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------

def print_parse_exception(exc, filename=None):
    msg = u"Parse Error "
    if filename:
        msg += "while compiling {0}".format(filename)
    msg += ": " + exc.msg + "\n"
    msg += exc.line + "\n"
    msg += u" "*(exc.column-1) + u"^"
    print msg


def walk_folder(root=u'.'):
    for subdir, dirs, files in os.walk(root):
        reldir = subdir.lstrip(root).lstrip(u'/')
        for filename in files:
            yield os.path.join(reldir, filename)


def open_file(path, mode='rb', create_dir=False, create_mode=0755):
    # Opens the given path. If create_dir is set, will
    # create all intermediate folders necessary to open
    try:
        newfile = open(path, mode)
    except IOError:
        # end here if not create_dir
        if not create_dir:
            raise
        newfile = None

    if not newfile:
        # may raise OSError
        filedir = os.path.split(path)[0]
        os.makedirs(filedir, create_mode)
        newfile = open(path, mode)

    return newfile


def copy_file(src, dst, create_dir=True, create_mode=0755):
    try:
        shutil.copy2(src, dst)
    except IOError:
        if not create_dir:
            raise
        # may raise OSError
        filedir = os.path.split(dst)[0]
        os.makedirs(filedir, create_mode)
        shutil.copy2(src, dst)


def matches_pattern(pattern, filepath):

    def _is_match(pattern_list, token_list):
        if not pattern_list or not token_list:
            return False
        i, j = 0, 0
        while True:
            if pattern_list[j] == '**':
                if j+1 == len(pattern_list): return True
                if _is_match(pattern_list[j+1:], token_list[i:]):
                    return True
                else:
                    i+=1 
            elif fnmatch.fnmatch(token_list[i], pattern_list[j]):
                i+=1
                j+=1
            else:
                return False
            if i==len(token_list) and j==len(pattern_list):
                return True
            if i==len(token_list) or j==len(pattern_list):
                return False

    return _is_match(pattern.strip('/').split('/'), 
                     filepath.strip('/').split('/'))
