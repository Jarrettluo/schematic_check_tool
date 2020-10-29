import re
import csv
import pandas as pd

# 检查文件输入
# check_rule_file = 'UPS_AUTO_check_rule_v2.2.csv'

# net_list_file = 'UPS_AUTO_V2.2.tel'
# 检查项目从4到8
csv_rule_from = 4
csv_rule_to = 8

# 创建引脚类
class Pin:
    def __init__(self, name_ini, comp_ini, net_ini):
        self.name = name_ini
        self.comp = comp_ini
        self.net = net_ini

# 创建器件类
class Comp:
    def __init__(self, RefDes_ini, part_num_ini, Pins_list_ini):
        self.name = RefDes_ini
        self.part_num = part_num_ini
        self.pins = Pins_list_ini

# 创建网络类
class Net:
    def __init__(self, name_ini, Pins_list_ini):
        self.name = name_ini
        self.pins = Pins_list_ini

# 第一步：读取所有器件引脚数量，返回字典
def read_all_pin(check_rule_file):
    """
    读取规则文件，并返回结果
    :param check_rule_file:
    :return:
    """
    csv_reader = csv.reader(open(check_rule_file))  # 读取文件
    dict_pin_num = {}   # 返回的器件对应引脚数量字典
    try:
        for list in csv_reader:
            dict_pin_num[list[0]] = list[3] # 保留器件和引脚数量映射关系
        del dict_pin_num['part_num']    # 删除第一行无关项
        return dict_pin_num # 返回字典
    finally:
        print("read_all_pin 资源收回！")

# 第二步，读取tel文件
def read_tel_file(net_list_file, dict_pin_num, pins, comps, nets):
    """
    读取网表文件，并进行
    :param net_list_file:
    :param dict_pin_num:
    :param pins:
    :param comps:
    :param nets:
    :return:
    """
    # 读取文件
    file_object = open(net_list_file, 'r')
    try:
        # 第三步，读取网表中的PACKAGES
        dict_RefDes = read_packages(file_object, dict_pin_num, pins, comps, nets)
        print(dict_RefDes)
        # 第四步，读取网表中的NETS
        dict_pins = read_nets(file_object, pins, comps, nets)
        print(dict_pins)
    finally:
        print("read_tel_file 资源收回！")
        file_object.close()
    return

# 第三步，读取网表中的PACKAGES
def read_packages(file_object, dict_pin_num, pins, comps, nets):
    # 全局变量
    packages_flag = 0  # packages部分停止记录标记
    nets_flag = 0  # nets部分停止记录标记
    comma_flag = False
    RefDes_temp = ''
    part_num_temp = ''
    dict_RefDes = {}
    # 建立正则表达库
    p_money_start = re.compile('^\$.*')
    p_packages = re.compile('^\$PACKAGES$')
    p_nets = re.compile('^\$NETS$')
    p_extract_package_0 = re.compile('!\s\'.*\'\s;')
    p_extract_package_1 = re.compile('!\s\'[\w-]*\'\s!')
    p_extract_RefDes = re.compile(';\s.*')
    p_find_comma = re.compile('.*,\n$')
    # 从Package开始，全局遍历，提取Part Number与位号关系
    for line in file_object:
        # 满足$PACKAGE正则要求时，开始记录
        if p_packages.match(line) is not None:
            packages_flag = 1
            print(line)
        # 不满足$PACKAGE正则要求，但满足其他$正则要求，跳出循环
        elif p_money_start.match(line) is not None:
            break
        # 保证不会输出空
        part_num = ''
        RefDes = ''
        # 开始记录时运行
        if (packages_flag == 1) & (p_packages.match(line) is None):
            # 满足!和;之间要求
            if p_extract_package_0.search(line):
                # 同时满足!和!之间要求
                if p_extract_package_1.search(line):
                    # 提取!和!之间内容，即part number
                    part_num = p_extract_package_1.search(line).group()
                    # print(part_num) # 调试
                # 仅满足!和;之间要求
                else:
                    # 提取!和;之间内容，即part number
                    part_num = p_extract_package_0.search(line).group()
                    # print(part_num) # 调试
                # 去掉无关字符
                part_num = part_num.strip('!')
                part_num = part_num.strip(';')
                part_num = part_num.strip('\s')
                RefDes = RefDes.strip('\n')
                part_num = part_num[2:-2]
            # 发现是位号行或者有逗号flag
            if p_extract_RefDes.search(line) or comma_flag:
                # 如果发现带逗号或继续有逗号
                if p_find_comma.search(line):
                    # 如果是该part第一行
                    if p_extract_RefDes.search(line):
                        RefDes = p_extract_RefDes.search(line).group()  # 提取第一行位号
                        part_num_temp = part_num  # 保存至全局变量
                    # 如果不是第一行
                    elif comma_flag:
                        RefDes = line  # 添加改行到RefDes
                    # 去掉无关字符
                    RefDes = RefDes.strip(';')
                    RefDes = RefDes.strip('\s')
                    RefDes = RefDes.strip('\n')
                    RefDes = RefDes.strip(',')
                    RefDes_temp = RefDes_temp + " " + RefDes  # 保存至全局变量
                    comma_flag = True  # 设置为发现逗号flag
                    continue  # 跳出本行，继续查找
                # 如果没有再发现逗号，并且在逗号flag下
                elif comma_flag:
                    # 从全局变量下取出
                    RefDes = RefDes_temp + " " + line
                    part_num = part_num_temp
                    # 清空全局变量，推出逗号flag
                    RefDes_temp = ''
                    part_num_temp = ''
                    comma_flag = False
                # 如果没有逗号，则直接记录
                else:
                    RefDes = p_extract_RefDes.search(line).group()
                    # 去掉无关字符
                    RefDes = RefDes.strip(';')
                    RefDes = RefDes.strip('\s')

                # 最终输出
                # print(part_num + RefDes)  # 调试
                list_RefDes = RefDes.split()    # 字符串分割成列表
                dict_RefDes[part_num] = list_RefDes # 存在字典里

                # 添加引脚对象、添加器件对象
                add_pin_comp_obj(dict_pin_num, part_num, list_RefDes, pins, comps, nets)
                # print(dict_RefDes)  # 调试
    return dict_RefDes

# 第四步，读取网表中的NETS
def read_nets(file_object, pins, comps, nets):
    # 全局变量
    nets_flag = 0  # nets部分停止记录标记
    comma_flag = False
    pin_name_temp = ''
    net_name_temp = ''
    dict_pins = {}
    # 建立正则表达库
    p_money_start = re.compile('^\$.*')
    p_nets = re.compile('^\$NETS$')
    p_extract_net_0 = re.compile('\'.*\'\s;')
    p_extract_pin_name = re.compile(';\s.*')
    p_find_comma = re.compile('.*,\n$')
    # 从Package开始，全局遍历，提取Part Number与位号关系
    for line in file_object:
        # 满足$NETS正则要求时，开始记录
        if p_nets.match(line) is not None:
            nets_flag = 1
            print(line)
        # 不满足$PACKAGE正则要求，但满足其他$正则要求，跳出循环
        elif p_money_start.match(line) is not None:
            break
        # 保证不会输出空
        net_name = ''
        pin_name = ''
        # 开始记录时运行
        if (nets_flag == 1) & (p_nets.match(line) is None):
            # 满足;之前要求
            if p_extract_net_0.search(line):
                # 提取;之前内容，即net_name
                net_name = p_extract_net_0.search(line).group()
                # 去掉无关字符
                net_name = net_name.strip(';')
                net_name = net_name.strip('\s')
                pin_name = pin_name.strip('\n')
                net_name = net_name[1:-2]
            # 发现是位号行或者有逗号flag
            if p_extract_pin_name.search(line) or comma_flag:
                # 如果发现带逗号或继续有逗号
                if p_find_comma.search(line):
                    # 如果是该part第一行
                    if p_extract_pin_name.search(line):
                        pin_name = p_extract_pin_name.search(line).group()  # 提取第一行位号
                        net_name_temp = net_name  # 保存至全局变量
                    # 如果不是第一行
                    elif comma_flag:
                        pin_name = line  # 添加改行到RefDes
                    # 去掉无关字符
                    pin_name = pin_name.strip(';')
                    pin_name = pin_name.strip('\s')
                    pin_name = pin_name.strip('\n')
                    pin_name = pin_name.strip(',')
                    pin_name_temp = pin_name_temp + " " + pin_name  # 保存至全局变量
                    comma_flag = True  # 设置为发现逗号flag
                    continue  # 跳出本行，继续查找
                # 如果没有再发现逗号，并且在逗号flag下
                elif comma_flag:
                    # 从全局变量下取出
                    pin_name = pin_name_temp + " " + line
                    net_name = net_name_temp
                    # 清空全局变量，推出逗号flag
                    pin_name_temp = ''
                    net_name_temp = ''
                    comma_flag = False
                # 如果没有逗号，则直接记录
                else:
                    pin_name = p_extract_pin_name.search(line).group()
                    # 去掉无关字符
                    pin_name = pin_name.strip(';')
                    pin_name = pin_name.strip('\s')
                #print(net_name + pin_name)  # 调试
                list_pins = pin_name.split()    # 字符串分割成列表
                dict_pins[net_name] = list_pins # 存在字典里

                add_net_obj(net_name, list_pins, pins, comps, nets)
                # print(dict_pins)  # 调试
    return dict_pins

# 提取列表中的所有值
def get_list_value(dict):
    return_list = []
    for value in dict.values():
        return_list.append(value)
    return return_list

# 添加引脚和器件对象函数
def add_pin_comp_obj(dict_pin_num, part_num, list_RefDes, pins, comps, nets):
    ############ 添加引脚对象 ############
    # 找出该器件引脚数量
    # print(part_num)
    pin_count = dict_pin_num.get(part_num)
    comp_count = len(list_RefDes)
    # 逐一赋值
    for i in range(0, comp_count):
        pins_temp = []
        comp_name = list_RefDes[i]
        # 每个器件，逐一添加引脚后缀
        for j in range(1, int(pin_count) + 1):
            pin_name = list_RefDes[i] + "." + str(j)
            pins[pin_name] = Pin(pin_name, comps["NA"], nets["NA"])  # 创建Pin对象，添加到字典
            pins_temp.append(pins[pin_name])    # 添加到临时列表中
        ############ 添加器件对象 ############
        comps[comp_name] = Comp(comp_name, part_num, pins_temp)  # 创建Comp对象，添加到字典
        ############ 更新引脚中的器件对象 ############
        update_pin_obj(pins_temp, comps[comp_name], 0)
    return True

# 添加网络对象函数，更新引脚对象
def add_net_obj(net_name, list_pins, pins, comps, nets):
    ############ 添加网络对象 ############
    # 找出该网络引脚数量
    # pin_count = len(list_pins)
    # print("Debug0: " + str(net_name))
    # print("Debug1: " + str(pin_count))
    pins_temp = []
    # 每个网络，逐一添加引脚后缀
    for pin_name in list_pins:
        # print("Debug2: " + pin_name)
        pins_temp.append(pins[pin_name])    # 添加到临时列表中
        pins[pin_name].net = nets["NA"]
    ############ 添加器件对象 ############
    nets[net_name] = Net(net_name, pins_temp)  # 创建网络对象，添加到字典
    ############ 更新引脚中的网络对象 ############
    update_pin_obj(pins_temp, nets[net_name], 1)
    return True

# 更新引脚中的对象
def update_pin_obj(list_in, obj_in, obj_flag):
    for obj_pin in list_in:
        # print("debug0: " + obj_pin.name)
        # 传入为器件
        if obj_flag == 0:
            # print("debug: " + obj_pin.name + " " + obj_pin.comp.name)
            obj_pin.comp = obj_in
        # 传入为网络
        if obj_flag == 1:
            # print("debug: " + obj_pin.name + " " + obj_pin.net.name)
            obj_pin.net = obj_in
    return True

# 调试函数
def result_debug(pins, comps, nets):
    ########## 调试pins #########
    print("===================== 调试pins =====================")
    for ii in range(0, len(get_list_value(pins))):
        pin = get_list_value(pins)[ii]
        print(pin.name + " " + pin.comp.name + " " + pin.net.name)
    print("===================== 调试pins =====================")
    ########## 调试pins #########

    ########## 调试comps #########
    print("===================== 调试comps =====================")
    for jj in range(0, len(get_list_value(comps))):
        str_comp_pins = ""
        component = get_list_value(comps)[jj]
        for value in component.pins:
            str_comp_pins = str_comp_pins + " " + value.name
        print(component.name + " " + component.part_num + " " + str_comp_pins)
    print("===================== 调试comps =====================")
    ########## 调试comps #########

    ########## 调试nets #########
    print("===================== 调试nets =====================")
    for kk in range(0, len(get_list_value(nets))):
        str_net_pins = ""
        net = get_list_value(nets)[kk]
        for value in net.pins:
            str_net_pins = str_net_pins + " " + value.name
        print(net.name + " " + str_net_pins)
    print("===================== 调试nets =====================")
    ########## 调试nets #########

# NA元素写入
def initial_NA(pins, comps, nets):
    pins["NA"] = Pin("NA", "NA", "NA")
    comps["NA"] = Comp("NA", "NA", [pins["NA"]])
    nets["NA"] = Net("NA", [pins["NA"]])
    pins["NA"] = Pin("NA", comps["NA"], nets["NA"])
    return True

# 读取CSV，提取规则列表：｛"TD301DCAN.1": [1,1,0,0]｝
def csv2PinRule(check_rule_file):
    csv_reader = csv.reader(open(check_rule_file))  # 读取文件
    check_list = {}  # 返回的引脚检查项字典
    try:
        for list in csv_reader:
            value_list = []
            key = list[0] + "." + list[1]   # 键为：part_name.pin_number
            # 目前四个检查项范围
            for i in range(csv_rule_from,csv_rule_to):
                if list[i] == "TRUE":
                    value_list.append(1)    # True为1
                elif list[i] == "FALSE":
                    value_list.append(0)    # False为0
                else:
                    if key != "part_num.pin_num":
                        print(key + "在csv引脚规则有误！")  # 首行不检查，检测到有问题的报错
            check_list[key] = value_list  # 保留规则和引脚数量映射关系
        del check_list["part_num.pin_num"]  # 删除第一行
        # print(check_list) # 调试
        return check_list  # 返回字典
    finally:
        print("csv2PinRule 资源收回！")

# 输入引脚名，根据规则列表，输出规则检查列表，返回checklist中对应的值，part_name.pin_number对应的[True, False....]
def extract_pin_rule(pin_name, pins, check_list):
    pin_obj = pins[pin_name]    # 根据Pin名称，得到Pin对象
    part_num = pin_obj.comp.part_num    # 得到器件名称
    p_pin_num = re.compile('\.\d+$')    # 得到.及以后数字
    pin_num = p_pin_num.search(pin_name).group()    # 搜索匹配到的字符串
    pin_temp = part_num + str(pin_num)  # 加上part number输出
    # print("debug: " + pin_temp) # 调试
    return check_list[pin_temp]

# 引脚引出规则，返回{'引脚名'：True/False}
def pin_out_rule(pins, check_list):
    pins_result = {}    # 返回的引脚检查结果
    for key in pins:
        if key != "NA":
            list_out = extract_pin_rule(key, pins, check_list)  # 找出规则检查项是否为1
            if list_out[0] == 1:
                # 当网络名称为NA，说明没有联网，违规
                if pins[key].net.name != "NA":
                    pins_result[key] = False    # 合规返回False
                    # print(key + ": Pass!")
                else:
                    pins_result[key] = True    # 违规返回True
                    print(key + ": Failed!")
    return pins_result

# 输出网络-元器件表，返回{'网络名'：[元器件列表]}
def net_comp_map(nets):
    sorted_nets = sorted(nets)  # 网络名排序
    return_dict = {}
    for key in sorted_nets:
        # 该网络名不是NA，新建字典及其列表
        if key != "NA":
            comps_list = []
            pins_temp = nets[key].pins  # 提取该网络中的引脚
            for pin in pins_temp:
                comps_list.append(pin.comp.name)    # 逐个添加引脚名
            comps_list.sort()   # 器件名排序
            return_dict[key] = comps_list
    return return_dict

# 网络-引脚名错误对照表，输入引脚错误结果，返回{'网络名'：[引脚名列表]}
def result_pin_2_net(nets, pins, result_dict):
    # 添加返回字典
    net_dict = {}
    # 每个网络均建立，在字典中添加空列表
    for net in nets:
        if net != "NA":
            net_dict[net] = []
    # 遍历结果列表
    for key in result_dict:
        # 该引脚违规且网络名不是NA，字符串加入列表中
        if result_dict[key] == True and pins[key].net.name != "NA":
            net_dict[pins[key].net.name].append(pins[key].name)
    return net_dict

# 元器件-引脚名错误对照表，输入引脚错误结果，返回{'RefDes'：[引脚名列表]}
def result_pin_2_comp(comps, pins, result_dict):
    # 添加返回字典
    comp_dict = {}
    # 每个器件均建立，在字典中添加空列表
    for comp in comps:
        if comp != "NA":
            comp_dict[comp] = []
    # 遍历结果列表
    for key in result_dict:
        # 该引脚违规且网络名不是NA，字符串加入列表中
        if result_dict[key] == True and pins[key].comp.name != "NA":
            comp_dict[pins[key].comp.name].append(pins[key].name)
    return comp_dict

# 主函数
def check(check_rule_file, net_list_file):
    ########## 解析网表和CSV #########
    # 新建字典
    pins = {}
    comps = {}
    nets = {}
    # NA元素写入
    initial_NA(pins, comps, nets)
    # 第一步：读取所有器件引脚数量，返回字典
    dict_pin_num = read_all_pin(check_rule_file)
    # 第二步，读取tel文件
    read_tel_file(net_list_file, dict_pin_num, pins, comps, nets)
    # debug：打印解析网表的结果
    result_debug(pins, comps, nets)
    # 最后一步，生成网络-器件关系表
    chart1 = net_comp_map(nets)
    # print(net_comp_map(nets))

    ########## 检查过程 #########
    # csv检查项表缓存至内存
    check_list = csv2PinRule(check_rule_file)
    # 检查引脚是否引出
    pin_out_result = pin_out_rule(pins, check_list)
    # 打印结果，违规返回True，合规返回False
    # print("Violation Result: " + str(pin_out_result))

    ########## 输出对照结果 #########
    # 打印网络-违规引脚对照表
    # print(result_pin_2_net(nets, pins, pin_out_result))
    # 打印元器件-违规引脚对照表
    chart2 = result_pin_2_comp(comps, pins, pin_out_result)
    # print(result_pin_2_comp(comps, pins, pin_out_result))

    df1 = pd.DataFrame([chart1]).T
    df1[0] = df1[0].apply(lambda x: ','.join(x))

    df2 = pd.DataFrame([chart2]).T
    df2[0] = df2[0].apply(lambda x: None if x == [] else ','.join(x))
    df2.dropna(axis=0, how='any', thresh=None, subset=None, inplace=True)
    return df1, df2