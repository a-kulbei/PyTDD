#!/usr/bin/python -tt

import re
import os.path

class Method:
    def __init__(self, name, numberArgs = 0):
        assert(len(name) > 0)
        self._name = name
        self._numberArgs = numberArgs
        self._signature = ""

    def get_name(self):
        return self._name

    def get_args(self):
        return self._args

    def get_signature(self):
        if len(self._signature) == 0:
            self._signature = self._construct_signature()
        
        return self._signature

    def _construct_signature(self):
        signature = self._name + "(self"

        for i in range(self._numberArgs):
            signature += ", arg" + str(i + 1)

        signature += ")"

        return signature


class Class:
    def __init__(self, name, pathToFile):
        self._name = name
        self._pathToFile = pathToFile
        self._methods = []

    def add_method(self, name, numberArgs):
        pass
        #assert(len(name) > 0)
        # TODO - maybe assert that name is valid for Python

        #method = Method(name, numberArgs)

        #sed_cmd = "sed s/signature/'" + method.get_signature() + "'/ " + Templates.methodStub + " >> " + self._pathToFile

        #Utils.run_command(sed_cmd)

        #self._methods.append(method)

        #return method

class ClassMenager:

    def __init__(self):
        pass

    @staticmethod
    def get_method_text(name, numberArgs):

        method = Method(name, numberArgs)

        return Templates.get_method_text(method.get_signature())

    @staticmethod
    def get_class_text(name):
        # TODO: it should be possible to generate class signature with
        # inheretance and constructor with few args

        return Templates.get_class_text(name)

class Templates:
      
    @staticmethod
    def get_class_text(className):

        file = open("templates/class.py", 'rU')
        content = file.read()

        return content.replace("ClassName", className)

    @staticmethod
    def get_method_text(signature):

        file = open("templates/method.py", 'rU')
        content = file.read()

        return content.replace('signature', signature)