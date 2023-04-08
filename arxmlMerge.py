from builtins import *
import sys
import os
import glob
from lxml import etree
from copy import deepcopy
import logging
log_file = None
logging.basicConfig(
    filename=log_file,
    format="%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.DEBUG
    #  level=logging.INFO,
    # level=logging.WARNING
)
Logger=logging.getLogger()

def clear_name_space(tag):
    for elem in tag.getiterator():
        # Skip comments and processing instructions,
        # because they do not have names
        if not (
            isinstance(elem, etree._Comment)
            or isinstance(elem, etree._ProcessingInstruction)
        ):
            # Remove a namespace URI in the element's name
            elem.tag = etree.QName(elem).localname

def merge_arxml(src_element = None, dst_element = None, namespace='', currentPath='', arDict='', current_tag_path=''):
    '''
        合并src_element 的信息到dst_element中
        1. src_element.tag 一定和dst_element.tag 一致
        1. 先查看pakge 是否同名, 不同名则新增
        Note: 必须查询到孙节点才能判定合并规则
    '''

    for src_child in src_element:
        # 先查看下面有没有包含 name的包,包名是不是一致
        # 如果有name的包， 且包名，tag名一致
        src_name_tag = src_child.find('./' + namespace + 'SHORT-NAME')
        #  src_pkg_list = src_child.xpath("//*[SHORT-NAME[text()='" + src_name_tag.text + "']]")
        if src_name_tag is not None :
            #子节点有Name名,package  name合并
            #  nodes = dst_element.xpath("//*[SHORT-NAME[@sid='3' and text()='text']]")
            dst_pkg_list = dst_element.xpath("./*[SHORT-NAME[text()='" + src_name_tag.text + "']]")
            if(dst_pkg_list):
                currentPath = currentPath + "/" + src_name_tag.text
                current_tag_path=''
                if(len(dst_pkg_list) > 1):
                    info = src_name_tag.text+"同名节点过多"
                    Logger.warning('info='+str(info))
                merge_arxml(src_element = src_child,
                        dst_element=dst_pkg_list[0],
                        namespace=namespace,
                        currentPath=currentPath,
                        arDict='',
                        current_tag_path=current_tag_path)
            else:
                dst_element.append(deepcopy(src_child))
                continue
        else:
            # 子节点没有Name

            # 先判定子节点是不是包含文本的最末节点

            attr_keys = src_child.attrib.keys()
            if len(attr_keys) > 0:
                if("UUID" in attr_keys): attr_keys.remove("UUID")
            key = ''
            key_val = ''
            if len(attr_keys) > 0:
                key = attr_keys[0]
                key_val = src_child.get(key)


            find_str = ""+src_child.tag
            if(key):
                find_str = find_str+"[@"+key+"='"+key_val+"']"

            has_child = True 
            src_txt = src_child.text.strip()
            if (src_txt):
                has_child = False
                find_str = find_str+"[. = '"+ src_txt +"']"

            Logger.debug('find_str='+str(find_str))
            #  dst_pkg_list = dst_element.xpath(find_str)
            # 节点下还有子节点, 查询tag 和attr就行
            dst_pkg_list = dst_element.xpath(find_str)
            if(dst_pkg_list):
                if(len(dst_pkg_list) > 1):
                    info = currentPath+' : '+find_str+"超过一个"
                if(has_child):
                    merge_arxml(src_element = src_child,
                            dst_element=dst_pkg_list[0],
                            namespace=namespace,
                            currentPath=currentPath,
                            arDict='',
                            current_tag_path=current_tag_path+'/'+src_child.tag)
            else:
                dst_element.append(deepcopy(src_child))
    pass


def main():
    sys.argv.append("D:/gcbb/xiaomi/EMB/main/arxml/ApplIfDefine/arxml_bsw")
    sys.argv.append("tmp.arxml")
    if len(sys.argv) < 3:
        print("syntax: %s inputFolder outputfile" % sys.argv[0])
        exit()

    folder = sys.argv[1]
    files = glob.glob(folder + "/*.arxml")

    Logger.debug('files='+str(files))

    tree = etree.parse(files[0])
    targetRoot = tree.getroot()

    clear_name_space(targetRoot)

    print ("target " + files[1])
    for filename in files[1:]:
        print ("Merge " + filename)
        tree = etree.parse(filename)
        root = tree.getroot()
        clear_name_space(root)
        merge_arxml(
            src_element = root,
            dst_element = targetRoot,
            currentPath='',
            current_tag_path='')
    
    outfile = open(sys.argv[2], "wb")
    print(sys.argv[2])
    outfile.write(etree.tostring(targetRoot, pretty_print=True))
    outfile.close()

if __name__ == '__main__':
    sys.exit(main())
