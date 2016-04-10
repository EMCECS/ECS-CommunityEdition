# coding=utf-8


class PersistentState(object):
    
    
    
    def load(self):
        """
        Load current state (may be empty)
        :raises IOError: if filesystem exceptions prevent config file read or initial write
        """
        logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
        if self.state_file is None:
            pass
        else:

            template_vars = {}.update(self.config.toDict())
            if self.script_file is not None:
                template_vars.update(self.script.toDict())

            try:
                self.state_dataset = DataSet(self.state_file,
                                             additional_template_vars=template_vars)
                logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name)
                logobj(self.state_dataset.content)
                self.state = DotMap(self.state_dataset.content)
                logobj(self.state)
            except IOError as e:
                logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': ' + repr(e))
                # must be a new install or else we don't have permissions.
                # Try to create an empty config and see what happens.
                try:
                    self.state_dataset = DataSet(self.state_file, create_if_missing=True,
                                                 additional_template_vars=template_vars)
                    logobj(self.state_dataset.content)
                    self.state = DotMap(self.state_dataset.content)
                    logobj(self.state)
                except IOError as cf:
                    logging.debug(self.__class__.__name__ + ': ' + sys._getframe().f_code.co_name + ': ' + repr(cf))
                    print("Unable to create a new state file: " + repr(cf))
                    # and presumably crash, though at some point we should tell
                    # the user to make sure they're mounting /opt correctly in Docker
                    raise
                