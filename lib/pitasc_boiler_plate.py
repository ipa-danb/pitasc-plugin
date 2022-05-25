#!/usr/bin/env python

import pitasc.model
from pitasc.parameter_model import ParameterBasic, ParameterDict, ParameterModel, ParameterList
from cppitasc.package_path import get_package_path

## python
from collections import OrderedDict, ChainMap
import copy
import argparse
import json
import rospy

## pitasc


class Loader():
    def __init__(self, file_paths = []):
        self.file_paths = file_paths
        self.elements = ['skill', 'monitor', 'script']
        self.file_paths.append(get_package_path('pitasc_library') + '/models/skills.xml')
        self.desc = pitasc.model.Model()
        for path in self.file_paths:
            self.desc.import_file(path)
        self.build_skill_tree()

    def build_skill_tree(self):
        self.skill_tree = ChainMap(*[self.build_tree(e) for e in self.elements])
        return self.skill_tree

    def build_tree(self, type_name):
        hate_count = 0
        skill_tree = {}
        for parameter in self.desc.root.find_models(type_name):
            para_tree = {}
            for param in parameter.data.values():
                #print(type(param), param.parameter_id)
                if type(param) is ParameterBasic:
                    try:
                        # print(param.parameter_id, type(param))
                        pt = str(param.data_type)
                        try:
                            if type(param.data) is OrderedDict:
                                continue
                            else:
                                pd = str(param.data).replace('[','').replace(']','').replace("'",'')
                        except Exception:
                            pd = None
                        para_tree[str(param.parameter_id)] = {'data': pd, 'description': pt}
                        #print({'data': pd, 'description': pt})
                    except Exception:
                        hate_count += 1
                        print(" ^^^ i hate this parameter\n")
                        print("----------------------------")
                        raise
                elif type(param) is ParameterList:
                    if param.parameter_id in ['skills', 'monitors', 'scripts']:
                        para_tree[str(param.parameter_id)] = {'data': '\n\t', 'description': f'List : Enter {param.parameter_id} here'}
            skill_tree[parameter.parameter_id] = copy.deepcopy(para_tree)
            skill_tree[parameter.parameter_id]["desc"] = parameter.meta.data["description"].data
        return skill_tree

    def build_xml_segment(self, name):
        rab = copy.copy(self.skill_tree[name])
        # startzeile:
        building_pattern = str('')
        building_pattern += '<!-- {} -->\n'.format(rab.pop('desc'))
        building_pattern += '<clone id="{0}" prototype="{0}">\n'.format(name)
        rab.pop('skill_name', None)
        for element in rab:
            building_pattern += '\t<!--member: {0} type: {1} -->\n'.format(element, rab[element]['description'])
            building_pattern += '\t<member id="{0}">{1}</member>\n'.format(element, rab[element]['data'])
        building_pattern += "</clone>\n"

        return building_pattern

    def save_to_file(self, output_file_name='pitasc.dump'):
        save_dict = {}
        for element in self.skill_tree:
            save_dict[element] = self. build_xml_segment(element)

        with open(output_file_name, 'w') as f:
            json.dump(save_dict, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="get xml for pitasc skill")
    parser.add_argument('package_paths',nargs='*', type=str)
    parser.add_argument('-o','--output_file', type=str, default='pitasc.dump', required=False)
    args = parser.parse_args()
    lir = Loader(args.package_paths)
    lir.save_to_file(args.output_file)
