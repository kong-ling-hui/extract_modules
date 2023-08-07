import re
import os
import argparse
import yaml
import shutil

class Mod:
    def __init__(self, name):
        self.name = name
        ###判断是否有两个不同的父模块
        self.is_common = False
        ###父模块
        self.father_module = set()
        ###模块存放的路径
        self.dir = ""

def get_config(my_prefix, config_file):
    with open(config_file) as config:
        conf = yaml.load(config, Loader=yaml.FullLoader)
        dirs = conf.keys()
        for dir in dirs:
            dir = my_prefix + '/' + dir
            if not os.path.exists(dir):
                os.makedirs(dir)
    os.makedirs(os.path.join(my_prefix, "Common"))
    os.makedirs(os.path.join(my_prefix, "Top"))
    return conf

def main():    
    parser = argparse.ArgumentParser(description='verilog module extractor, seperate every single module within a single verilog file')

    parser.add_argument('--file', '-f', dest="file", type=str, help='input verilog file', default=r'./data/SimTop.sv')
    parser.add_argument('--output', '-o', dest="out_dir", type=str, help='output directory', default=r'./des')
    parser.add_argument('--config', '-c', dest="config_file", type=str, help='config file', default=r'./config.yml')
    parser.add_argument("--output_count_prefix", '-p', dest="prefix", action="store_true", help="enable output file prefix with current module count")
    

    args = parser.parse_args()
    prefix = args.prefix
    assert args.file != None
    assert args.out_dir != None
    assert args.config_file !=None
    
    file = os.path.abspath(args.file)
    out_dir = os.path.abspath(args.out_dir)
    config_file = os.path.abspath(args.config_file)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    file_path = os.path.dirname(os.path.abspath(file))
    file_name = os.path.basename(file)

    os.system('rm -rf '+ out_dir + '/' + '*' )
    ####
    my_prefix = out_dir
    config = get_config(my_prefix, config_file)
    dict_of_modules = dict()
    ####
    
    # pdb.set_trace()
    with open(file, 'rt') as f:
        find_module = False
        find_endmodule = False
        module_name = ''
        wf = None
        lf = open(file_path+f'/{file_name}.log', 'wt')
        module_count = 0
        line_num = 1
        for line in f:
            # pdb.set_trace()
            if(line.count('module') != 0 and find_module == False):
                find_module = True
                module_name = re.split(r'[;,\s(]\s*',line)[1]
                
                ###
                dict_of_modules[module_name] = Mod(module_name)
                ###
                
                module_count = module_count + 1
                strr = '['+str(module_count)+'] find module => '+module_name + ' in line ' + str(line_num)
                # print(strr)
                print(strr, file=lf)
                if prefix:
                    file_name = out_dir + '/' + str(module_count) + '_' + module_name + '.sv'
                else:
                    file_name = out_dir + '/' + module_name + '.sv'
                print(file_name)
                wf = open(file_name,'wt')
                
            if(line.count('endmodule') != 0):
                find_endmodule = True

            if(find_module == True):
                print(line,end='',file=wf)
                temp_line = re.split(r'[;,\s]\s*',line)
                if(temp_line.count('(') == 1 and temp_line.count(')') == 0):
                    # print(temp_line)
                    # strr = '\tfind submodule => ('+temp_line[1] +')\t('+ temp_line[2] +') in line ['+str(line_num)+']'
                    strr = '\tfind submodule => module_name:( %-*s)  inst_name:( %-*s) in line [ %-*s ]'%(20,temp_line[1],20,temp_line[2],6,str(line_num))
                    # print(strr)
                    
                    ###
                    if temp_line[1] not in dict_of_modules.keys():
                        dict_of_modules[temp_line[1]] = Mod(temp_line[1])
                    dict_of_modules[temp_line[1]].father_module.add(module_name)
                    if(len(dict_of_modules[temp_line[1]].father_module) >= 2):
                        dict_of_modules[temp_line[1]].is_common = True
                    ###
                    print(strr, file=lf)     
            if(find_endmodule == True):
                find_module = False
                find_endmodule = False
                strr = module_name +' done!' + ' in line ' + str(line_num) + '\n'
                # print(strr)
                print(strr,file=lf)
                try:
                    wf.close()
                except:
                    pass
            line_num = line_num + 1
        lf.close()
        # os.system('rm '+output_path+'.v')
    ##add file list
    # for key in dic.keys():
    #     with open(f'{my_prefix}/{key}/aaafilelist.txt', 'wt') as filelist:
    #         for value in dic[key]:
    #             print(value, end='\n', file=filelist)
    
    #根据yaml文件操作
    for key in config.keys():
        mv_dir_dst = os.path.join(out_dir, key)
        for value in config[key]:
            mv_dir_src = os.path.join(out_dir, value + ".sv")
            if dict_of_modules[value].is_common == True:
                #move to common
                mv_dir_dst = os.path.join(out_dir, "Common")
            shutil.move(mv_dir_src, mv_dir_dst)
    
    #yaml文件中没有描述的统一放到Top文件夹中
    pattern = r".+\.sv$"
    for a in os.listdir(out_dir):
        if(re.match(pattern, a)):
            shutil.move(os.path.join(out_dir, a), os.path.join(out_dir, "Top"))
    
    

if __name__ == '__main__': main()
