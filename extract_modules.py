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
        ###子模块
        self.submodules = set()

def get_config(my_prefix, config_file):
    with open(config_file) as config:
        conf = yaml.load(config, Loader=yaml.FullLoader)
        dirs = conf
        for dir in dirs:
            dir = my_prefix + '/' + dir
            if not os.path.exists(dir):
                os.makedirs(dir)
            with open(os.path.join(dir, "aafilelist.txt"), "w"):
                pass
    os.makedirs(os.path.join(my_prefix, "Common"))
    os.makedirs(os.path.join(my_prefix, "Top"))
    with open(os.path.join(my_prefix, "Common/aafilelist.txt"), "w"):
        pass
    with open(os.path.join(my_prefix, "Top/aafilelist.txt"), "w"):
        pass
    return conf
###这里的dict_of_modules可能是值传递
###一个参数是字典，另一个参数是.yml文件中指明的模块
###.yml中指明模块的所有子模块，包括子模块的子模块依次递归
def get_all_submodules(dict_of_modules, conf):
    all_submodules = []
    for file_module in conf:
        all_submodules.clear()
        try:
            if(file_module not in dict_of_modules.keys()):
                raise Exception(f"[WARNING] Don't have module '{file_module}', please modify the configuration file")
            ###判断submodules是否为空，为空则continue
            # print(file_module, dict_of_modules[file_module].submodules)
            if(not bool(dict_of_modules[file_module].submodules)):
                continue
            all_submodules.extend(list(dict_of_modules[file_module].submodules))
            for submodule in all_submodules:
                all_submodules.extend(list(dict_of_modules[submodule].submodules))
            dict_of_modules[file_module].submodules.update(set(all_submodules))
        except Exception as e:
            conf.remove(file_module)
            print(str(e))
    

def main():    
    parser = argparse.ArgumentParser(description='verilog module extractor, seperate every single module within a single verilog file')

    parser.add_argument('--file', '-f', dest="file", type=str, help='input verilog file', default=r'./data')
    parser.add_argument('--output', '-o', dest="out_dir", type=str, help='output directory', default=r'./des')
    parser.add_argument('--config', '-c', dest="config_file", type=str, help='config file', default=r'./config.yml')
    parser.add_argument("--output_count_prefix", '-p', dest="prefix", action="store_true", help="enable output file prefix with current module count")
    

    args = parser.parse_args()
    prefix = args.prefix
    assert args.file != None
    assert args.out_dir != None
    assert args.config_file !=None
    
    file_path = os.path.abspath(args.file)
    out_dir = os.path.abspath(args.out_dir)
    config_file = os.path.abspath(args.config_file)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    os.system('rm -rf '+ out_dir + '/' + '*' )
    ####
    my_prefix = out_dir
    config = get_config(my_prefix, config_file)
    dict_of_modules = dict()
    ####
    ##获取所有.v .sv文件
    all_files = []
    pattern = r".+\.(sv|v)$"
    for listdir_file in os.listdir(file_path):
        if(re.match(pattern, listdir_file)):
            all_files.append(listdir_file)
    
    for myfile in all_files:
        file_name = myfile
        file = os.path.join(file_path, file_name)
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
                        strr = '\tfind submodule => module_name:( %-*s)  inst_name:( %-*s) in line [ %-*s ]'%(20,temp_line[1],20,temp_line[2],6,str(line_num))
                        
                        ###
                        if temp_line[1] not in dict_of_modules.keys():
                            dict_of_modules[temp_line[1]] = Mod(temp_line[1])
                        dict_of_modules[temp_line[1]].father_module.add(module_name)
                        if(len(dict_of_modules[temp_line[1]].father_module) >= 2):
                            dict_of_modules[temp_line[1]].is_common = True
                        #存一下当前模块的子模块
                        dict_of_modules[module_name].submodules.add(temp_line[1])
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
            
    ########
    get_all_submodules(dict_of_modules, config)
    for module in config:
        mv_dir_dst = os.path.join(out_dir, module)
        try:
            for sub in dict_of_modules[module].submodules:
                mv_dir_src = os.path.join(out_dir, sub + ".sv")
                if dict_of_modules[sub].is_common == True:
                    #move to common
                    mv_dir_dst = os.path.join(out_dir, "Common")
                    flag = True
                try:
                    shutil.move(mv_dir_src, mv_dir_dst)
                    with open(os.path.join(mv_dir_dst, "aafilelist.txt"), "a") as f:
                        print(sub, file = f)
                except Exception as e:
                    # print(str(e))
                    pass
        except Exception as e:
            print(f"[WARNING] Don't have module {str(e)}, please modify the configuration file")
    
    #yaml文件中没有描述的统一放到Top文件夹中
    pattern = r".+\.(sv|s)$"
    for a in os.listdir(out_dir):
        if(re.match(pattern, a)):
            shutil.move(os.path.join(out_dir, a), os.path.join(out_dir, "Top"))
            with open(os.path.join(out_dir, "Top/aafilelist.txt"), "a") as f:
                    print(a.split(".")[0], file = f)

if __name__ == '__main__': main()
