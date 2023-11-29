import sys
import subprocess
import re
from enum import Enum,IntEnum


data = {}

class State(IntEnum):
    INIT = 1
    SYNC_RESP = 2
    SYNC_UPDATE = 3

class UpdateLine(Enum):
    RT = "ReceivedTime"
    RTS = "ReceivedTimeStr"
    ALS = "Alias"
    TGT = "Target" 
    TSS = "TimestampStr"
    TS = "Timestamp"
    DPL = "Duplicate"
    PATH = "Path"
    VAL = "JSON_VAL"
    V_RT = "Resource_Type"
    V_AID = "AID"
    V_PV = "pm-value"
    V_PVMIN = "pm-min"
    V_PVMAX = "pm-max"
    V_PVAVG = "pm-avg"
    V_PVUNT = "pm-unit"
    V_END = "END"
    RT_DPL = "RT_DPL"
    ALS_SYNC = "ALS_SYNC"

class KEYS(Enum):
    TOTAL = "total"
    UPDATES = "updates"
    UPDATE = "update"
    UPSTATE = "upstate"
    SYNC_RESP = "sync_resp"
    PATH = "path"
    ERROR = "error"
    RT = "rtime"
    RTS = "rtimeS"
    T = "time"
    TS = "timeS"
    LN = "lineNo"
    TIME = "timestamp"
    INIT = "initial"



TIME_FORMAT = "\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?\+\d\d:\d\d"


def check_one_update(line, lineNo, state):
    if state[KEYS.UPSTATE] == UpdateLine.RT:
        state[KEYS.UPDATE][KEYS.LN]=lineNo
        match = re.match("^first.*receivedTime = (\d+)$", line)
        if match:
            tmpupdate = {}
            timestamp = {}
            timestamp[KEYS.RT]=match.group(1)
            tmpupdate[KEYS.LN]=lineNo
            tmpupdate[KEYS.TIME]=timestamp
            tmpupdate[KEYS.PATH]=None
            state[KEYS.UPDATE]=tmpupdate
            state[KEYS.UPSTATE]=UpdateLine.RTS
            if state[KEYS.TOTAL] == State.SYNC_RESP:
                state[KEYS.TOTAL] = State.SYNC_UPDATE
        else:
            state[KEYS.UPDATE][KEYS.ERROR]="yes"
            print(f"Line {lineNo}: {UpdateLine.RT} is expected and not")
    elif state[KEYS.UPSTATE] == UpdateLine.RT_DPL:
        match = re.match("^first.*receivedTime = (\d+)$", line)
        match1 = re.match("^first.*duplicates.*$", line)
        if match:
            state[KEYS.UPSTATE]=UpdateLine.RT
            check_one_update(line,lineNo,state)
        elif match1:
            state[KEYS.UPSTATE]=UpdateLine.DPL
            check_one_update(line,lineNo,state)
        else:
            state[KEYS.UPDATE][KEYS.ERROR]="yes"
            print(f"Line {lineNo}: {UpdateLine.RT_DPL} is expected and not")
    elif state[KEYS.UPSTATE] == UpdateLine.RTS:
        match = re.match(f"^first.*receivedTimeStr = ({TIME_FORMAT})$", line)
        if match:
            state[KEYS.UPDATE][KEYS.TIME][KEYS.RTS]=match.group(1)
            if state[KEYS.TOTAL] == State.INIT:
                state[KEYS.UPSTATE]=UpdateLine.ALS_SYNC
            else:
                state[KEYS.UPSTATE]=UpdateLine.ALS
        else:
            state[KEYS.UPDATE][KEYS.ERROR]="yes"
            print(f"Line {lineNo}: {UpdateLine.RTS} is expected and not")
    elif state[KEYS.UPSTATE] == UpdateLine.ALS_SYNC:
        match = re.match("^first.*alias.*$", line)
        match1 = re.match("^first.*sync_response = true$", line)
        if match:
            state[KEYS.UPSTATE]=UpdateLine.TGT
        elif match1:
            print(f"Line {lineNo}: sync_response is received")
            state[KEYS.SYNC_RESP][KEYS.RT] = state[KEYS.UPDATE][KEYS.TIME][KEYS.RT]
            state[KEYS.SYNC_RESP][KEYS.RTS] = state[KEYS.UPDATE][KEYS.TIME][KEYS.RTS]
            state[KEYS.UPDATE]={}
            state[KEYS.TOTAL]=State.SYNC_RESP
            state[KEYS.UPSTATE]=UpdateLine.RT
        else:
            state[KEYS.UPDATE][KEYS.ERROR]="yes"
            print(f"Line {lineNo}: {UpdateLine.ALS_SYNC} is expected and not")
    elif state[KEYS.UPSTATE] == UpdateLine.ALS:
        match = re.match("^first.*alias.*$", line)
        if match:
            state[KEYS.UPSTATE]=UpdateLine.TGT
        else:
            state[KEYS.UPDATE][KEYS.ERROR]="yes"
            print(f"Line {lineNo}: {UpdateLine.ALS} is expected and not")
    elif state[KEYS.UPSTATE] == UpdateLine.TGT:
        match = re.match("^first.*prefix.target.*$", line)
        if match:
            state[KEYS.UPSTATE]=UpdateLine.TSS
        else:
            state[KEYS.UPDATE][KEYS.ERROR]="yes"
            print(f"Line {lineNo}: {UpdateLine.TGT} is expected and not")
    elif state[KEYS.UPSTATE] == UpdateLine.TSS:
        match = re.match(f"^first.*timeStampStr = ({TIME_FORMAT})$", line)
        if match:
            state[KEYS.UPSTATE]=UpdateLine.TS
            state[KEYS.UPDATE][KEYS.TIME][KEYS.TS]=match.group(1)
        else:
            state[KEYS.UPDATE][KEYS.ERROR]="yes"
            print(f"Line {lineNo}: {UpdateLine.TSS} is expected and not")
    elif state[KEYS.UPSTATE] == UpdateLine.TS:
        match = re.match(f"^first.*timestamp = (\d+)$", line)
        if match:
            state[KEYS.UPSTATE]=UpdateLine.DPL
            state[KEYS.UPDATE][KEYS.TIME][KEYS.T]=match.group(1)
        else:
            state[KEYS.UPDATE][KEYS.ERROR]="yes"
            print(f"Line {lineNo}: {UpdateLine.TS} is expected and not")
    elif state[KEYS.UPSTATE] == UpdateLine.DPL:
        match = re.match("^first.*duplicates.*$", line)
        if match:
            state[KEYS.UPSTATE]=UpdateLine.PATH
        else:
            state[KEYS.UPDATE][KEYS.ERROR]="yes"
            print(f"Line {lineNo}: {UpdateLine.DPL} is expected and not")
    elif state[KEYS.UPSTATE] == UpdateLine.PATH:
        match = re.match(f"^first.*path\.elem = /pm/real-time-pm-data/(.*)$", line)
        if match:
            state[KEYS.UPSTATE]=UpdateLine.VAL
            state[KEYS.UPDATE][KEYS.PATH]=match.group(1)
        else:
            state[KEYS.UPDATE][KEYS.ERROR]="yes"
            print(f"Line {lineNo}: {UpdateLine.PATH} is expected and not")
    elif state[KEYS.UPSTATE] == UpdateLine.VAL:
        match = re.match("^first.*val = JSON_IETF_VAL:{$", line)
        if match:
            state[KEYS.UPSTATE]=UpdateLine.V_RT
        else:
            state[KEYS.UPDATE][KEYS.ERROR]="yes"
            print(f"Line {lineNo}: {UpdateLine.VAL} is expected and not")
    elif state[KEYS.UPSTATE] == UpdateLine.V_RT:
        match = re.match(f'\s+"resource-type":\s+".*",$', line)
        state[KEYS.UPSTATE]=UpdateLine.V_AID
        if not match:
            state[KEYS.UPDATE][KEYS.ERROR]="yes"
            match = re.match('^}$', line)
            if match:
                print(f"Line {lineNo}: Empty block body unexpected received for path {state[KEYS.UPDATE][KEYS.PATH]}")
                state[KEYS.UPSTATE]=UpdateLine.V_END
                check_one_update(line,lineNo,state)
            else:
                print(f"Line {lineNo}: {UpdateLine.V_RT} is expected and not")
    elif state[KEYS.UPSTATE] == UpdateLine.V_AID:
        match = re.match(f'\s+"AID":\s+".*",$', line)
        state[KEYS.UPSTATE]=UpdateLine.V_PV
        if not match:
            state[KEYS.UPDATE][KEYS.ERROR]="yes"
            print(f"Line {lineNo}: {UpdateLine.V_AID} is expected and not")
    elif state[KEYS.UPSTATE] == UpdateLine.V_PV:
        match = re.match(f'\s+"pm-value":\s+"[0-9.-]+",$', line)
        state[KEYS.UPSTATE]=UpdateLine.V_PVMIN
        if not match:
            state[KEYS.UPDATE][KEYS.ERROR]="yes"
            print(f"Line {lineNo}: {UpdateLine.V_PV} is expected and not for path {state[KEYS.UPDATE][KEYS.PATH]}")
            check_one_update(line,lineNo,state)
    elif state[KEYS.UPSTATE] == UpdateLine.V_PVMIN:
        match = re.match(f'\s+"pm-value-min":\s+"[0-9.-]+",$', line)
        match1 = re.match(f'\s+"pm-unit":\s+".*"$', line)
        if match:
            state[KEYS.UPSTATE]=UpdateLine.V_PVMAX
        elif match1:
            state[KEYS.UPSTATE]=UpdateLine.V_END
        else:
            state[KEYS.UPDATE][KEYS.ERROR]="yes"
            state[KEYS.UPSTATE]=UpdateLine.V_PVMAX
            print(f"Line {lineNo}: {UpdateLine.V_PVMIN} or {UpdateLine.V_PVUNT} is expected and not")
            check_one_update(line,lineNo,state)
    elif state[KEYS.UPSTATE] == UpdateLine.V_PVMAX:
        match = re.match(f'\s+"pm-value-max":\s+"[0-9.-]+",$', line)
        state[KEYS.UPSTATE]=UpdateLine.V_PVAVG
        if not match:
            state[KEYS.UPDATE][KEYS.ERROR]="yes"
            print(f"Line {lineNo}: {UpdateLine.V_PVMAX} is expected and not for path {state[KEYS.UPDATE][KEYS.PATH]}")
            check_one_update(line,lineNo,state)
    elif state[KEYS.UPSTATE] == UpdateLine.V_PVAVG:
        match = re.match(f'\s+"pm-value-avg":\s+"[0-9.-]+",$', line)
        state[KEYS.UPSTATE]=UpdateLine.V_PVUNT
        if not match:
            state[KEYS.UPDATE][KEYS.ERROR]="yes"
            print(f"Line {lineNo}: {UpdateLine.V_PVAVG} is expected and not")
            check_one_update(line,lineNo,state)
    elif state[KEYS.UPSTATE] == UpdateLine.V_PVUNT:
        match = re.match(f'\s+"pm-unit":\s+".*"$', line)
        state[KEYS.UPSTATE]=UpdateLine.V_END
        if not match:
            state[KEYS.UPDATE][KEYS.ERROR]="yes"
            print(f"Line {lineNo}: {UpdateLine.V_PVUNT} is expected and not")
            check_one_update(line,lineNo,state)
    elif state[KEYS.UPSTATE] == UpdateLine.V_END:
        match = re.match('^}$', line)
        if match:
            state[KEYS.UPSTATE]=UpdateLine.RT_DPL
            tmp_update = state[KEYS.UPDATES].get(state[KEYS.UPDATE][KEYS.PATH])
            if tmp_update is None:
                tmp_update = {}
                tmp_update[KEYS.INIT]=[]
                tmp_update[KEYS.SYNC_RESP]=[]
                state[KEYS.UPDATES][state[KEYS.UPDATE][KEYS.PATH]]=tmp_update
            if state[KEYS.TOTAL] == State.INIT:
                tmp_update[KEYS.INIT].append(state[KEYS.UPDATE][KEYS.TIME])
            else:
                tmp_update[KEYS.SYNC_RESP].append(state[KEYS.UPDATE][KEYS.TIME])
        else:
            state[KEYS.UPDATE][KEYS.ERROR]="yes"
            print(f"Line {lineNo}: {UpdateLine.V_END} is expected and not")
    else:
        print(f"Line {lineNo}: {line} is unexpected line for an update")


def printUpdateTime(times: [], myfile):
    preT = 0
    preRT = 0
    first_time = -1
    i=0
    for t in times:
        t1 = int(t[KEYS.T])
        t1s = t[KEYS.TS]
        if i == 0:
            t2 = int(sys.argv[2])*1000
        else:
            t2 = (t1-preT)//1000000
        t3 = int(t[KEYS.RT])
        t3s = t[KEYS.RTS]
        t4 = t3-preRT
        if first_time < 0:
            first_time = t1
        base_time = first_time + i*int(sys.argv[2])*1000000000
        t5 = (t1-base_time)//1000000
        print(f"\t{t1}\t\t{t2}\t\t{t3}\t\t{t4}\t\t{t5}") 
        preT = t1
        preRT = t3
        if myfile:
            myfile.write(f"{t1//1000000} {t1s} {t3} {t3s} {t2} {t3-preRT}\n")
        i += 1



def getID(name: str):
    obj = name
    ids = None
    if "[" in name:
        parts = name.split("[")
        obj=parts[0]
        ids = ".".join([id.split("=")[1][0:-1] for id in parts[1:]])
    return (obj,ids)

def simplifyPmPath(path: str):
    d = path.split("direction=")[1].split("]")[0]
    l = path.split("location=")[1].split("]")[0]
    p = path.split("parameter=")[1].split("]")[0]
    if ":" in p:
        p=p.split(":")[1]
    # r = path.split("resource=")[1].split("/")[-1][0:-1]
    rl = path.split("resource=")[1].split("/")
    obj,id = getID(rl[-1][0:-1])
    idl=[obj]
    for s in [ getID(ss)[1] for ss in rl[0:-1]]:
        if s:
            idl.append(s)
    if id:
        idl.append(id)
    r="-".join(idl)

    return f"{r}_{p}_{d}_{l}"

state_m = {KEYS.TOTAL: State.INIT, 
        KEYS.UPSTATE: UpdateLine.RT, 
        KEYS.UPDATE : {}, 
        KEYS.UPDATES : {},
        KEYS.SYNC_RESP : {}}
l=1
with open(sys.argv[1],'r') as f:
    for line in f:
        if "Please input what do you" in line or "gnmi-client" in line or "io.grpc" in line :
            l += 1
            continue
        if len(line.strip()) == 0:
            l += 1
            continue
        if line.startswith("-----") or line.startswith("*"):
            l += 1
            continue
        check_one_update(line,l, state_m)
        l += 1
sync_resp_time = state_m[KEYS.SYNC_RESP][KEYS.RT]
sync_resp_timeS = state_m[KEYS.SYNC_RESP][KEYS.RTS]
found_error = False
if not sync_resp_time or not sync_resp_timeS:
    found_error = True
    print("SYNC_ERROR: No sync_response received")
init_num=1
samp_num=-1
all_updates = state_m[KEYS.UPDATES]
pathsI = set()
pathsII = set()
pathS = {}
for key in all_updates:
    spath = simplifyPmPath(key)
    print(f"{spath}:")
    times = all_updates[key]
    printUpdateTime(times[KEYS.INIT],None)
    print(f"\t{sync_resp_time}------------------")
    with open(f"{spath}.timer", "w") as f:
        printUpdateTime(times[KEYS.SYNC_RESP], f)
    tmp_init_num = len(times[KEYS.INIT])
    if tmp_init_num > 0:
        pathsI.add(spath)
    tmp_samp_num = len(times[KEYS.SYNC_RESP])
    if tmp_samp_num > 0:
        pathsII.add(spath)
    if samp_num < 0:
        samp_num = tmp_samp_num
    if tmp_init_num != init_num:
        found_error = True
        print(f"UPDATE_NUM_ERROR: received more than 1 init update [{tmp_init_num}] for path {key}")
    if tmp_samp_num != samp_num:
        found_error = True
        print(f"UPDATE_NUM_ERROR: received {tmp_samp_num} sample update [{samp_num}] for path {key}")
print("Paths before sync_response:")
[print(f"\t\t{pp}") for pp in sorted(pathsI)]
print("Paths after sync_response:")
[print(f"\t\t{pp}") for pp in sorted(pathsII)]
print(f"update number: init[{init_num}] and sample[{samp_num}]")
print(f"path number [INIT]: {len(pathsI)}  and path number [SYNC]:{len(pathsII)}")
