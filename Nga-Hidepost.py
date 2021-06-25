import nga_sdk
import time
import os

nga = nga_sdk.NGA()
if 'setting' in os.listdir('.'):#获取历史记录,tid,fid
    print('已获得历史记录（申请删帖楼tid,自组删帖目标版面fid,如需重置，请删除同目录的setting文件即可')
    setting1=open('setting','r')
    setting2=setting1.read()
    change=0
    selfhidetid=''
    selfhidefid=''
    lastsearch=''
    for read1 in setting2:
        if read1=='\n':
            change=change+1
            continue
        if change==0:
            selfhidetid=selfhidetid+read1
        elif change==1:
            selfhidefid=selfhidefid+read1
        elif change==2:
            lastsearch=lastsearch+read1
    setting1.close()
else:#初始化
    print('请输入自助删除贴的tid')
    selfhidetid=str(input())
    print('请输入需要删除帖子目标版面的fid')
    selfhidefid=str(input())
    lastsearch='0'
    setting1=open('setting','w')
    setting1.write(selfhidetid)
    setting1.write('\n')
    setting1.write(selfhidefid)
    setting1.write('\n')
    setting1.write(lastsearch)
    setting1.close()
    selfhidefid=int(selfhidefid)

finalresult=nga.get_single_post(selfhidetid)#将tid替换为自助申请楼的tid
#自助删帖申请楼tid

#获得本次处理开始楼层
print('上次处理到的楼层为:'+lastsearch+'L，是否直接使用该数据继续处理,若确定输入"Y",否则输入继续开始处理的楼层的阿拉伯数字,如11')
new=str(input())
if new!='Y':
    lastsearch=new
    
t=time.localtime()
logsfilename=time.strftime("%Y-%m-%d %H%M%S",t)
path=os.path.join('.\\logs\\'+logsfilename+'.txt')
logs=open(path,'w')

        
for i in finalresult['replys']:#获取楼层数及内容
    if int(i)<=int(lastsearch):
        continue
    authorid=finalresult['replys'][i]['authorid']
    content=finalresult['replys'][i]['content']
    stop=True
    tid=[]
    tid1=''
    for k in content:#获取TID，将所有获得的TID写入至列表tid
        if k=='=' or stop==False:
            if k=='=':
                stop=False
            if k!='=' and k!='[': 
                tid1=tid1+k
            if k=='[':
                stop=True
                tid.append(tid1)
                tid1=''
    count1=0
    count2=0
    for j in tid:#读取列表tid
        check=nga.get_single_post(j)
        if check['replys']['0']['authorid']!=authorid:#核对申请人和申请贴的楼主是否为同一个人
            access=False
            err1='i'+'L '+'tid='+j+',非申请人所发，已拒绝操作'
            print(err1)
            logs.write(err1+'\n')
            count2=count2+1
            continue
        if check['post']['fid']!=int(selfhidefid):#核对帖子是否在目标版面,将fid替换为招募版面或目标帖子版面
            access=False
            err2=i+'L '+'tid='+j+',帖子不在目标版面，已拒绝操作'
            print(err2)
            logs.write(err2+'\n')
            count2=count2+1
            continue
        if check['replys']['0']['authorid']==authorid and check['post']['fid']==int(selfhidefid):#将fid替换为招募版面或目标帖子版面
            #执行删帖操作
            nga.set_hide(j)
            count1=count1+1
    if count2==0:
        mess1=i+'L全部完成操作'
        print(mess1)
        print()
        logs.write(mess1+'\n'+'\n')
    else:
        mess2=i+'L完成'+str(count1)+'次,失败'+str(count2)+'次'
        print(mess2)
        print()
        logs.write(mess2+'\n'+'\n')
logs.close()
setting1=open('setting','w')
setting1.write(selfhidetid+'\n')
setting1.write(str(selfhidefid)+'\n')
setting1.write(i)
setting1.close()
        
        
    
         
    
    




