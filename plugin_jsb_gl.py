#!/usr/bin/python
# ----------------------------------------------------------------------------
# Plugin to generate OpenGL ES 2.0 / WebGL code for JSB
#
# Author: Ricardo Quesada
# Copyright 2013 (C) Zynga, Inc
#
# License: MIT
# ----------------------------------------------------------------------------
'''
Plugin to generate OpenGL ES 2.0 / WebGL code for JSB
'''

__docformat__ = 'restructuredtext'


# python modules
import re

# plugin modules
from generate_jsb import JSBGenerateFunctions

#
#
# OpenGL ES 2.0 / WebGL function plugin
#
#
class JSBGenerateFunctions_GL(JSBGenerateFunctions):

    def __init__(self, config):
        super(JSBGenerateFunctions_GL, self).__init__(config)

        # Extend supported types
        self.args_js_special_type_conversions['TypedArray0'] = [self.generate_argument_typedarray, 'void*']

    def generate_argument_typedarray(self, i, arg_js_type, arg_declared_type):
        if self._vectorFunction:
            t = 'js::ArrayBufferView::TYPE_FLOAT32' if self._vectorFunction.group(2) == 'f' else 'js::ArrayBufferView::TYPE_INT32'
            template = '\tGLsizei count;\n\tok &= jsval_typedarray_to_dataptr( cx, *argvp++, &count, &arg%d, %s);\n' % (i, t)
            self.fd_mm.write(template)
        else:
            raise Exception("Logic error in GL plugin")

    def generate_function_c_call_arg(self, i, dt):
        if self._vectorFunction and dt == 'TypedArray1':
            t = self._vectorFunction.group(2)
            cast = 'GLfloat' if t == 'f' else 'GLint'
            ret = ''
            if self._with_count:
                ret += ', count'
            ret += ', (%s*)arg%d ' % (cast, i)
            return ret
        return super(JSBGenerateFunctions_GL, self).generate_function_c_call_arg(i, dt)

    def validate_argument(self, arg):
        if self._vectorFunction:

            # Skip count
            if arg['name'] == 'count':
                return (None, None)

            # Vector thing
            if arg['type'] == '^i':
                return ('TypedArray0', 'TypedArray1')

        return super(JSBGenerateFunctions_GL, self).validate_argument(arg)

    def generate_function_binding(self, function):
        func_name = function['name']

        # Match for vector functions
        r = re.match('gl\S+([1-4])([fi])v$', func_name)
        self._vectorFunction = r
        self._with_count = (re.match('glVertexAttrib[1-4][fi]v', func_name) == None)

        return super(JSBGenerateFunctions_GL, self).generate_function_binding(function)
