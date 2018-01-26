import Queue
import threading
import time

import re
import Data_aquisition
import numpy as np
#polling_acquisition.py

class PollingAquisition():
  """
  #############################################################################
  Polling acqusisition framework with Queued data management
  """  

  """
  *****************
  VARIABLES
  """

  # operational vars
  _queue_size       = 1000 # number of items to queue
  _data_in_timeout    = 100 # ms
  _data_out_timeout   = 100 # ms
  _queue            = None 

  # threads
  _data_in_thread   = None
  _data_out_thread  = None

  # run flags
  _keep_running     = None
  _data_in_running  = None
  _data_out_running = None
  _running          = None

  # tracking
  _packets_read     = 0
  _packets_written  = 0

  _overflows        = 0
    
  
  

  """
  *****************
  API
  """
  
  def setup(self, size = None):
    """
    ---------------------------------------------------------------------------
    setup function, establish
    """
    if size:
      self._queue_size = size

    self._queue = Queue.Queue( maxsize = 100 )
    self._packets_read     = 0
    self._overflows        = 0

    return  True
  
  def start( self ):
    
    self._keep_running = True
    self._running = True

    self._packets_read     = 0
    self._overflows        = 0

    self._data_in_thread = threading.Thread( target = self._data_in_loop )
    self._data_in_thread.daemon = True 
    self._data_in_thread.start()

    self._data_out_thread = threading.Thread( target = self._data_out_loop )
    self._data_out_thread.daemon = True 
    self._data_out_thread.start()

    pass
  
  def stop( self ):
    self._keep_running = False
    
    if self._data_in_thread:
      # wait for thread to finish
      self._data_in_thread.join()
    self._data_in_thread = None

    if self._data_out_thread:
      #wait for thread to finish
      self._data_out_thread.join()
    self._data_out_thread = None

    self._running = False
    pass
  

  """
  *****************
  OVERRIDES
  """
  
  def read( self ):

      
    try:
        sensor_data = Data_aquisition.s.readline().decode("utf-8")
    except:
        print('ERROR: FAILED READING PORT')
        
            
    r = re.compile("([a-zA-Z]+)([0-9]+)")
    sensor_data = re.split('\t+', sensor_data)
    
    m = r.match(sensor_data[0])
    
    sensorType = m.group(1).decode('ascii')
    sensorID = m.group(2)
    
    if sensorType == 'EMG':
        sensor_data[0] = 10+float(sensorID)
    elif sensorType == 'IMU':
        sensor_data[0] = float(sensorID)
    
    sensor_data = [float(i) for i in sensor_data]
    sensor_data = np.asarray(sensor_data)
    
    Data_aquisition.dataStreamCheck(int(sensorID), sensorType)
    
    return sensor_data

  def write( self ):
    return 0 

  def shutdown( self ):
    return True  
  """
  *****************
  PRIVATES
  """

  def __init__( self ):
    """
    ---------------------------------------------------------------------------
    Constructor
    """
    pass

  def __del__( self ):
    """
    ---------------------------------------------------------------------------
    Make sure loops stop
    """
    self.stop()
    self.shutdown()
    pass

  def _data_in_loop( self ):
    """
    ---------------------------------------------------------------------------
    loop that polls for data
    """
    while( self._keep_running ):
      try:
        
        packet = self.read()
        self._queue.put( packet, True, self._data_in_timeout / 1000.0 )
        self._packets_read += 1
        
      except:
        #self._keep_running=False
        self._overflows += 1
        time.sleep( self._data_in_timeout / 1000.0)
        
        pass
      pass
    pass

  def _data_out_loop( self ):
    """
    ---------------------------------------------------------------------------
    loop that ships data out to destination
    """
    while( self._keep_running ):
      try:
        
        packet = self._queue.get( True, self._data_out_timeout / 1000.0 )
        self.write( packet )

        self._queue.task_done()
        
        self._packets_written +=1
        
      except:
        time.sleep( self._data_out_timeout / 1000.0)
        
        pass
      pass
    pass







