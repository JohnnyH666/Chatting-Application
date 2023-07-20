from src.data_store import data_store

def clear_v1():
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    store['messages'] = []
    store['dms'] = []
    store['workspace_stats'] = {'channels_exist':[],
                                'dms_exist':[],
                                'messages_exist': [],
                                'utilization_rate': 0,
                                }
    store['notifications'] = []
    store['removed'] = []
    data_store.set(store)
    return {}

