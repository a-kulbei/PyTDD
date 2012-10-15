import os.path
import sublime, sublime_plugin
import re

class CreateClassCommand(sublime_plugin.TextCommand):

    def _get_view(self, fileName):

        views = self.window.views()

        for view in views:
            if fileName == view.file_name():
                return view

        return None


    def run(self, edit):
        self.window = self.view.window()

        # get all selections in active view
        selections = self.view.sel() 

        # At the moment we are interesting only in first selection
        # TODO: Loop over all selections in the feature
        # Extract a class name
        if not selections[0].empty():
            self.className = self.view.substr(selections[0])
        else:
            return

        self.window.show_input_panel("Path to file", "", self.on_done, None, None)

    def on_done(self, fileName):
        # Firstly check that file exist
        if not os.path.exists(fileName):
            return # TODO we have to create this file in case it does not exist

        # Trying to find a view associated with this filename
        fileView = self._get_view(fileName)

        # if was not found let's open it
        if not fileView:
            fileView = self.window.open_file(fileName)

        classText = ClassMenager.get_class_text(self.className)

        fEdit = fileView.begin_edit()
        # TODO: at the moment there is an assumption that file is empty
        fileView.insert(fEdit, 0, classText)
        fileView.end_edit(fEdit)
	

class AddMethodCommand(sublime_plugin.TextCommand):

    def add_method(self, className, methodText, edit):
        window = self.view.window()

        regExp = "^\s*class\s*" + className + "[(]?[.\w)]*:$"

        # list of touples (View, region)
        points = []
        views = window.views()

        for view in views:
            regions = view.find_all(regExp)
            
            if regions:
                reg = view.line(regions[0])
                points.append((view, reg))

        # TODO: what to do in case few views were found
        if len(points) > 0:
            view = points[-1][0]
            reg = points[-1][1]
            edit = view.begin_edit()
            view.insert(edit, reg.end(), methodText)
            view.end_edit(edit)


    def get_class_name(self, points, selRegion):

        if len(points) < 0:
            return ""

        size = len(points)
        for i in range(size):
            reg = points[i][0]

            if selRegion.a - reg.a < 0:
                return points[i - 1][1]

        return points[-1][1]

    def _get_points(self, line, selection, edit):

        # Constractin the regExp with syntax:
        # <objectName>.<MethodName>()
        # obj name will be saved in the first regExp group
        regExp = "(\w+)\.(" + selection + ").*"
        match = re.search(regExp, line)

        if match:
            objName = match.group(1)
        else:
            return []

        # Trying to find object declaration
        # Syntax should something like:
        # <objName> = <ClassName>([args])
        # TODO: object may be returned by function, 
        # to think about how to deal with it
        regExp = "^\s*" + objName + "\s*=\s*(\w+)\(.*\).*$"
        regions = self.view.find_all(regExp)

        # Array of touples (region, className)
        points = []
        for reg in regions:
            region = self.view.line(reg)
            text = self.view.substr(region)

            # extraxt a class name by applying the same regExp
            match = re.search(regExp, text)
            if match:
                points.append((region, match.group(1)))

        return points


    def run(self, edit):

        selections = self.view.sel()
        sel = selections[0]

        # Do nothing if user forgot to select something
        if sel.empty():
            return

        # try to get a full line
        line = self.view.line(sel)
        lineText = self.view.substr(line)
        selText = self.view.substr(sel)

        # get all defenition in current view
        points = self._get_points(lineText, selText, edit)

        className = self.get_class_name(points, line)

        methodText = ClassMenager.get_method_text(selText, 0)
        self.add_method(className, methodText, edit)


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

        file = open("Templates/class.py", 'rU')
        content = file.read()

        return content.replace("ClassName", className)

    @staticmethod
    def get_method_text(signature):

        file = open("Templates/method.py", 'rU')
        content = file.read()

        return content.replace('signature', signature)
