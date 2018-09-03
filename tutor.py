import os
import torch

class Tutor:
    '''
    This is the class whose methods will be called
    to update queues and handle data I/O from
    main thread. This will be accessed by the I/O
    thread and by the main thread.

    Queues:
     - Backups
      + List of Dictionaries
     - Logs
      + List of Strings
     - Metrics Dictionary with M pairs
      + For each metric
       - List of floats/ints

     Class Variables:
       - Config Changes: hasLatestConfig boolean
       - Metrics Dictionary
       - Backups Dictionary
       - Logs List

     Functions(Setup):
      - Make Metric:
        + Args: (name)
        + Adds key and empty array
      - Create Config Template:
        + Args: List of tuples
        + Adds key and empty value
      - Model Instance:
        + Args: (model)
        + Saves backup using this model

     Functions(Input):
       - Create Backup(.backup)
        + Saves pickled data and model to backups
       - Log(.log)
        + Args: (string)
        + Adds String to Logs List
       - Metrics(.meter)
        + Args: (name, float/int)
        + Adds number to List

     Functions(Output):
      - Check for New Info(.check_info)
        + Args: (n) where n is length of client set
        + For Each Datastructure
         - Choose data by total len - n
         - Collect Data
         - Parse Data
         - Add to JSON Payload
        + Emit Payload to Client
      - Check for New Config(.check_config)
        + Args: ()
        + If not hasLatestConfig:
         - Run function to change Config
         - If backup is true, create backup
         - Set hasLatestConfig to True

      More Functions
        - Save state of Trainer(.save_state)
          + Args: ()
          + Save state of trainer as TXT:
            - Metric numbers
            - Logs
            - Config Parameters
        - Load state of Trainer(.load_state)
          + Args: (filename)
          + Parse State File:
            - Load Metric numbers
            - Load Logs
            - Load Config Parameters
        - Set Configuration to NN(User implemented):
          + Args: (config) where config is a dictionary
          + Changes hyperparameters, etc.
    '''
    def __init__(self,model,optimizer):

        self.model = model
        self.optimizer = optimizer
        self.hasLatestConfig = True
        self.backupID = 0
        self.currID = 0
        self.epoch = 0
        self.metrics = {}
        self.backups = []
        self.logs = []
        self.config = {}
        self.config_template = []
        if not os.path.exists('backups'):
            os.mkdir('backups')

    def make_metric(self,name):
        self.metrics[name] = []

    def make_config(self,tuples):
        '''
        List of Tuples
        Tuple:
        0: Name(string)
        1: Type(string)(boolean,range,string,option)
        2: Data:
          If boolean: Set to None
          If range: Set to (min,max,increment) *inclusive
          If string: Set to None
          If option: Set to names of options ('opt1','opt2',...)
        '''
        self.config_template = tuples
        for tuple in tuples:
            if tuple[1] == 'boolean':
                self.config[tuple[0]] = False
            elif tuple[1] == 'range':
                self.config[tuple[0]] = tuple[2][0]
            elif tuple[1] == 'string':
                self.config[tuple[0]] = ''
            elif tuple[1] == 'option':
                self.config[tuple[0]] = tuple[2][0]
            else:
                print(tuple[1],'is not a valid type!')

    def backup(self):
        state = {'epoch': self.epoch,
                 'model': self.model.state_dict(),
                 'optimizer': self.optimizer.state_dict()}
        for key,values in self.metrics.items():
            state[key] = values
        torch.save(state,'backups/backup_{:03d}.state'.format(self.backupID))
        self.backupID += 1
        state = {'ID': self.backupID,
                 'Epoch': self.epoch}
        for key,values in self.metrics.items():
            state[key] = values[-1]
        self.backups.append(state)

    def restore(self,ID):
        backup = torch.load('backups/backup_{:03d}.state'.format(ID))
        self.epoch = backup['epoch']
        self.model.load_state_dict(backup['model'])
        self.optimizer.load_state_dict(backup['optimizer'])
        for key,_ in self.metrics.items():
            self.metrics[key] = backup[key]
        self.currID = ID

    def log(self,string):
        self.logs.append(string)
        print(string)

    def meter(self,name,value):
        self.metrics[name].append(value)

    def check_info(self,clientn,ID):
        payload = {}
        if self.currID == ID:
            payload['reset'] = 'false'
            for key,values in self.metrics.items():
                indices = len(values)-clientn[key]
                if indices > 0:
                    payload[key] = values[-indices:]
                else:
                    payload[key] = []
        else:
            payload['reset'] = 'true'
            payload['ID'] = self.currID
            for key,values in self.metrics.items():
                payload[key] = values
        indices = len(self.backups)-clientn['backups']
        if indices > 0:
            payload['backups'] = self.backups[-indices:]
        else:
            payload['backups'] = []
        indices = len(self.logs)-clientn['logs']
        if indices > 0:
            payload['logs'] = self.logs[-indices:]
        else:
            payload['logs'] = []
        return payload

    def update_config(self,new_config):
        for tuple in self.config_template:
            if tuple[1] == 'boolean':
                self.config[tuple[0]] = new_config[tuple[0]].lower() == 'true'
            elif tuple[1] == 'range':
                self.config[tuple[0]] = float(new_config[tuple[0]])
            elif tuple[1] == 'string':
                self.config[tuple[0]] = new_config[tuple[0]]
            else:
                self.config[tuple[0]] = new_config[tuple[0]]
        self.hasLatestConfig = False
        if new_config['backup'].lower() == 'true':
            self.backup()

    def check_config(self):
        if not self.hasLatestConfig:
            return self.config
        else:
            return None
