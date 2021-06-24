import nga_sdk

nga = nga_sdk.NGA()
finalresult=nga.get_single_post('tid')#将tid替换为自助申请楼的tid
#自助删帖申请楼tid


for i in finalresult['replys']:#获取楼层数及内容
    if i=='0':
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
            print('i'+'L '+'tid='+j+',非申请人所发，已拒绝操作')
            count2=count2+1
            continue
        if check['post']['fid']!=fid:#核对帖子是否在目标版面,将fid替换为招募版面或目标帖子版面
            access=False
            print(i+'L '+'tid='+j+',帖子不在目标版面，已拒绝操作')
            count2=count2+1
            continue
        if check['replys']['0']['authorid']==authorid and check['post']['fid']==fid:#将fid替换为招募版面或目标帖子版面
            #执行删帖操作
            nga.set_hide(j)
            count1=count1+1
    if count2==0:
        print(i+'L全部完成操作')
        print()
    else:
        print(i+'L完成'+str(count1)+'次','，失败'+str(count2)+'次')
        print()
    
        
    
         
    
    




