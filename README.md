# extract_modules
extract verilog modules
运行程序需要三个参数，示例：
```
python extract_modules.py -f ./data -o ./des -c ./config.yml
```
`./data`该程序会处理该路径下的所有`.sv`和`.v`文件  
`./des`存储运行结果的路径，所有文件的后缀名都会变为`.sv`  
`./config.yml`配置文件  

![image](https://github.com/kong-ling-hui/extract_modules/blob/main/yaml.png)  
上图展示的是一个简单的yaml配置文件，运行之后会创建对应文件夹，然后将子模块放到对应的目录，下图是运行结果：  
![image](https://github.com/kong-ling-hui/extract_modules/blob/main/des_struct.png)  
其中所有的公共子模块则会放到Common下，其余模块都放到了Top文件夹里。  
