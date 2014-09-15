from threading import Lock, Thread
import time
import logging
import abc

from MemoryChecker import MemoryChecker

logger = logging.getLogger(__name__)

class IGolemVM:
    #######################
    def __init__( self ):
        pass

    #######################
    def getProgress( self ):
        assert False

    #######################
    def interpret( self, codeResource ):
        pass


class TaskProgress:
    #######################
    def __init__( self ):
        self.lock = Lock()
        self.progress = 0.0

    #######################
    def get( self ):
        with self.lock:
            return self.progress

    #######################
    def set( self, val ):
        with self.lock:
            self.progress = val


class GolemVM( IGolemVM ):
    #######################
    def __init__( self ):
        IGolemVM.__init__( self )
        self.srcCode = ""
        self.scope = {}
        self.progress = TaskProgress()

    #######################
    def getProgress( self ):
        return self.progress.get()
      
    #######################  
    def runTask( self, srcCode, extraData ):
        self.srcCode = srcCode
        self.scope = extraData
        self.scope[ "taskProgress" ] = self.progress

        return self._interpret()

    #######################
    @abc.abstractmethod
    def _interpret( self ):
        return

##############################################
class PythonVM( GolemVM ):
    def _interpret( self ):
        exec self.srcCode in self.scope
        return self.scope[ "output" ]


class PythonTestVM( GolemVM ):
    def _interpret( self ):
        mc = MemoryChecker()
        mc.start()
        try:
            exec self.srcCode in self.scope
        except Exception, e:
            logger.error("Execution failure {}".format( str( e ) ) )
        finally:
            estimatedMem = mc.stop()
        logger.info( "Estimated memory for taks: {}".format( estimatedMem ) )
        return self.scope[ "output" ], estimatedMem

