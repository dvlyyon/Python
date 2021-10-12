from nbi.restconf.client import RestconfSession 
import pdb
import time

def test_maxiumn_session():
    sessions = []
    try:
        for i in range(6):
            for j in range(200):
                session = RestconfSession('172.29.202.84','8181',f"admin{i}","e2e!Net4u#")
                s, r, d = session.connect()
                print (f"No.:{i}.{j} Status:{s} Reason:{r} Data:{d}")
                sessions.append(session)
        time.sleep(3600)
    finally:
        for s in sessions:
            s.close()

if __name__ == '__main__':
    test_maxiumn_session()
