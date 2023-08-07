# extract_modules
extract verilog modules
运行程序需要三个参数，示例：
```
python extract_modules.py -f ./SimTop.sv -o ./des -c ./config.yml
```
`./SimTop.sv`需要提取模块的源文件  
`./des`存储运行结果的路径  
`./config.yml`配置文件  

![image](https://github.com/kong-ling-hui/extract_modules/blob/main/yaml.png)  
上图展示的是一个简单的yaml配置文件，运行之后会创建Ctrl和Exu文件夹，然后将Ctrl和Exu下的模块放到对应的目录，下图是运行结果：  
![image](https://github.com/kong-ling-hui/extract_modules/blob/main/des_struct.png)  
其中Exu下的部分模块是公共子模块则会放到Common下，而且该程序只会处理配置文件中指出的模块，其余模块都放到了Top文件夹里。  
