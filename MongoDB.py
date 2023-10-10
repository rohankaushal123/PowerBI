#!/usr/bin/env python
# coding: utf-8

# In[22]:


import pandas as pd
import pymongo
import json
from bson import json_util,ObjectId
import time
import schedule
def main():
    connection_url='mongodb+srv://lohawalla:Rohan123@hrms-v2.0icliah.mongodb.net/?retryWrites=true&w=majority'
    client=pymongo.MongoClient(connection_url)
    db=client['test']
    WO_db=db['workorders']
    CH_db=db['childparts']
    FI_db=db['finisheditems']
    AT_db=db['v2attendances']
    cursor_WO=WO_db.find()
    cursor_CH=CH_db.find()
    cursor_FI=FI_db.find()
    cursor_v2=AT_db.find()
    dataWO=list(cursor_WO)
    dataCH=list(cursor_CH)
    dataFI=list(cursor_FI)
    data_v2=list(cursor_v2)
    WorkOrders=pd.DataFrame(dataWO)
    ChildParts=pd.DataFrame(dataCH)
    FinishedItems=pd.DataFrame(dataFI)
    ChildParts['consumedItem'] = ChildParts['consumedItem'].fillna(0)
    Attendance= pd.DataFrame(data_v2)
    empId = []
    punchIn = []    
    punchOut = []
    punchOutBy=[]
    punchInBy=[]
    status=[]
    for i, j in zip(Attendance['punches'], Attendance['status']):
        try:
            empId.append(i[0]['employeeId'])
            punchIn.append(i[0]['punchIn'])
            punchOut.append(i[0]['punchOut'])
            punchOutBy.append(i[0]['punchOutBy'])
            punchInBy.append(i[0]['punchInBy'])
            status.append(j)
        except (KeyError, IndexError):
            punchOut.append("-")


    
    attendance = pd.DataFrame(zip(empId, punchIn, punchOut,punchOutBy,punchInBy,status), columns=['EmpId', 'PunchIn', 'PunchOut','PunchOutBy','PunchInBy','status'])
    attendance['PunchIn'] = attendance['PunchIn'].fillna(pd.Timestamp('2023-01-01'))
    attendance['PunchOut'] = attendance['PunchOut'].fillna(pd.Timestamp('2023-01-01'))
    attendance['PunchOutBy'] = attendance['PunchOutBy'].fillna("-")
    attendance['PunchInBy'] = attendance['PunchOutBy'].fillna("-")
    MCode=[]
    ChildPart=[]
    Process=[]
    Quantity=[]
    Id=[]
    ChildPartId=[]
    ProcessId=[]
    for i,j,k in zip(FinishedItems['MCode'],FinishedItems['masterBom'],FinishedItems['_id']):
        Code=i
        _id=k
        for n in range(len(j)):
            ChildPartId.append(j[n]['childPart']['id'])
            ChildPart.append(j[n]['childPart']['childPartName'])
            Process.append(j[n]['process']['processName'])
            ProcessId.append(j[n]['process']['id'])
            Quantity.append(j[n]['quantity'])
            MCode.append(Code)
            Id.append(_id)
    Finished_Item=pd.DataFrame(zip(Id,MCode,ChildPartId,ChildPart,ProcessId,Process,Quantity),columns=['ID','MCode','ChildPart_ID','ChildPart','ProcessID','Process','Quantity'])
    WorkOrderId=[]
    ChildPartName=[]
    ProcessName=[]
    Quantity=[]
    for i,j in zip(WorkOrders['_id'],WorkOrders['masterBom']):
        for a in range(len(j)):
            WorkOrderId.append(i)
            ChildPartName.append(j[a]['partName'])
            ProcessName.append(j[a]['process'])
            Quantity.append(j[a]['numberOfItem'])
    WO_Quantity=pd.DataFrame(zip(WorkOrderId,ChildPartName,ProcessName,Quantity),columns=['WorkOrderID','ChildPartName','ProcessName','Quantity'])
    _id=[]
    PartName=[]
    MaterialCode=[]
    itemId=[]
    itemName=[]
    consumedQuantity=[]
    GodownId=[]
    CIunit=[]
    for i,j,k,l,a,b in zip(ChildParts['_id'],ChildParts['partName'],ChildParts['consumedItem'],ChildParts['materialCode'],ChildParts['unit'],ChildParts['productionGodown']):
        PN=j
        id_=i
        mcode=l
        cID=a
        GD=b
        if (k==[] or k==0):
            itemId.append('-')
            itemName.append('-')
            consumedQuantity.append('-')
            GodownId.append('-')
            CIunit.append(cID)
            _id.append(id_)
            PartName.append(PN)
            MaterialCode.append(mcode)
        else:
            for n in range(len(k)):
                itemId.append(k[n]['itemId'])
                itemName.append(k[n]['itemName'])
                consumedQuantity.append(k[n]['consumedItemQuantity'])
                GodownId.append(b)
                _id.append(id_)
                PartName.append(PN)
                MaterialCode.append(mcode)
                CIunit.append(cID)
    childparts=pd.DataFrame(zip(_id,PartName,MaterialCode,itemId,itemName,consumedQuantity,CIunit,GodownId),columns=['ID','PartName','MCode','ItemID','ItemName','ConsumedQuantity','CIunit','GodownId'])
    dataframes = {
        "ChildParts":childparts,
        "WO_Quantity":WO_Quantity,
        "Finished_Item":Finished_Item,
        "Attendance":attendance
    }
    for df_name, df_data in dataframes.items():
        db = client["POWERBI_DATA"]  
        collection = db[df_name]
        if collection.name in db.list_collection_names():
            db.drop_collection(collection.name)
        collection.insert_many(df_data.to_dict(orient="records"))
    client.close()

if __name__ == "__main__":
    main()
    schedule.every(15).minutes.do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)

 


